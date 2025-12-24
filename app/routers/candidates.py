from fastapi import APIRouter, status, Depends, HTTPException
from .. import models, schema, oauth2, database
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

router = APIRouter(prefix="/candidates/me", tags=["Candidates"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.CandidateOut)
def create_a_candidate_profile(candidate: schema.CandidateCreate, db: Session = Depends(database.get_db)):

    is_candidate_exit = db.query(models.Candidate).filter(models.Candidate.email == candidate.email).first()
    if is_candidate_exit:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Duplicate Candidate')

    hash_password = oauth2.get_password_hash(candidate.password)
    candidate.password = hash_password
    new_candidate = models.Candidate(**candidate.dict())

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return new_candidate

@router.get("", status_code=status.HTTP_200_OK, response_model=schema.CandidateOut)
def get_candidate_details(db : Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.id == current_user.id).first()
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate doesn't exist")
    return candidate

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_candidate(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.id == current_user.id)
    if candidate.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate is not found")
    candidate.delete(synchronize_session=False)
    db.commit() 

@router.put("", status_code=status.HTTP_200_OK, response_model=schema.CandidateOut)
def update_a_candidate(candidate: schema.CandidateUpdate, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    
    update_candidate = db.query(models.Candidate).filter(models.Candidate.id == current_user.id)

    existing_candidate = update_candidate.first()
    if existing_candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate doesn't exist")
    
    update_data = candidate.dict(exclude_unset=True)
    update_candidate.update(update_data, synchronize_session=False)
    db.commit()
    
    db.refresh(existing_candidate)
    return existing_candidate

@router.get("/my-applications", status_code=status.HTTP_200_OK, response_model=List[schema.JobApplicationWithDetails])
def get_my_applications(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    applications = db.query(models.CandidateJobApplication).filter(models.CandidateJobApplication.candidate_id == current_user.id).all()
    return applications
