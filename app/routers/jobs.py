from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schema
from typing import List, Optional
from .. import oauth2

router = APIRouter(prefix="/jobs", tags=['Jobs'])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.JobOut)
def create_a_job(job: schema.Job, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Only employer can create a job")

    new_job = models.Job(employer_id=current_user.id, **job.dict())
    
    if new_job.experience_end <= new_job.experience_start:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="experience start should be less than experience end - Wrong range")
    
    check_for_duplicate_job_entry = db.query(models.Job).filter(models.Job.job_title.contains(new_job.job_title) , (models.Job.experience_start == new_job.experience_start) , (models.Job.experience_end == new_job.experience_end), models.Employer.id == current_user.id)
    
    if check_for_duplicate_job_entry.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Job for position {new_job.job_title} already exists') 
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job) 
    return new_job

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def get_a_single_job(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'job with id: {id} is not found')
    return job

@router.get("/{title}", status_code=status.HTTP_200_OK, response_model=List[schema.JobOut])
def get_all_jobs(db: Session = Depends(get_db), limit: int=10, skip: int=0, title: str | None = None):
    jobs = db.query(models.Job)

    # apply the filter
    if title:
        jobs = jobs.filter(models.Job.jobTitle.contains(title))
    jobs = jobs.limit(limit).offset(skip).all()    
    return jobs

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_job(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Job Id : {id} doesnot exist')
    db.delete(job)
    db.commit()

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def update_job(id: int, job: schema.Job, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    updated_job = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id)
    if updated_job.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job Id : {id} doesn't exist")
    updated_job.update(job.dict(), synchronize_session=False)
    db.commit()
    return updated_job.first()


@router.post("/{id}/apply", status_code=status.HTTP_200_OK, response_model=schema.JobApplicationOut)
def apply_for_a_job(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # Check if the current user is candidate or not
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")

    # check if the job id exists or not
    job_exist = db.query(models.Job).filter(models.Job.id == id).first()
    if not job_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job doesn't exist")
    
    duplicate_entry = db.query(models.CandidateJobApplication).filter(models.CandidateJobApplication.candidate_id == current_user.id, models.CandidateJobApplication.job_id == id).first()
    if duplicate_entry:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidate has already applied for the job")
    
    application = models.CandidateJobApplication(job_id=id, candidate_id=current_user.id)
    db.add(application) 
    db.commit()
    db.refresh(application)
    return application

@router.get("/{id}/applicants", status_code=status.HTTP_200_OK, response_model=List[schema.JobApplicants])
def get_job_applicants(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    
    # Check whether the job exists or not
    job_exists = db.query(models.Job).filter(models.Job.id == id).first()
    if not job_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job doesn't exists")
    
    applicants = db.query(models.CandidateJobApplication).filter(models.CandidateJobApplication.job_id == id).all()
    if not applicants:
        raise HTTPException(status_code=status.HTTP_200_OK, detail='No one has applied for this job so far')
    return applicants




    
    



