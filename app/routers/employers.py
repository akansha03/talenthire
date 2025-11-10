from fastapi import APIRouter, status, Depends, HTTPException
from .. import schema
from ..database import get_db
from sqlalchemy.orm import Session
from .. import config, oauth2, models
from typing import List

router = APIRouter(prefix="/employers", tags = ["Employers"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.EmployerOut)
def create_an_employer(employer: schema.EmployerCreate, db: Session = Depends(get_db)):

    # First hash the password
    encrypted_pass = oauth2.get_password_hash(employer.password)
    employer.password = encrypted_pass
    new_employer = models.Employer(**employer.dict())

    db.add(new_employer)
    db.commit()
    db.refresh(new_employer)
    return new_employer

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schema.EmployerOut)
def get_an_employer(id: int, db: Session = Depends(get_db)):
    employer = db.query(models.Employer).filter(models.Employer.id == id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Employer with id : {id} doesn't exist")
    return employer

@router.get("", status_code=status.HTTP_200_OK, response_model=List[schema.EmployerOut])
def get_all_employers(db: Session = Depends(get_db), limit: int=10, skip: int=0, name: str | None = None):
    employer_query = db.query(models.Employer)
    if name:
        employers = employer_query.filter(models.Employer.orgName.contains(name))
    employers = employer_query.limit(limit).offset(skip).all()    
    return employers

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_an_employer(id: int, db: Session = Depends(get_db)):
    query_employer = db.query(models.Employer).filter(models.Employer.id == id)
    if not query_employer.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employer with id : {id} was not found')
    query_employer.delete(synchronize_session=False)
    db.commit()


