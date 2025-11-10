from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schema
from typing import List, Optional
from .. import oauth2

router = APIRouter(prefix="/jobs", tags=['Jobs'])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.JobOut)
def create_a_job(job: schema.JobCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):

    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only employer can create a job")

    new_job = models.Job(**job.dict())
    if new_job.experience_end <= new_job.experience_start:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="experience start should be less than experience end - Wrong range")
    
    check_for_duplicate_job_entry = db.query(models.Job).filter(models.Job.job_title.contains(new_job.job_title) , (models.Job.experience_start == new_job.experience_start) , (models.Job.experience_end == new_job.experience_end), models.Employer.id == current_user.id)
    print(check_for_duplicate_job_entry) 
    if check_for_duplicate_job_entry.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Job for position {new_job.job_title} already exists')
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job) 
    return new_job

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def get_a_single_job(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'job with id: {id} is not found')
    return job 

@router.get("", status_code=status.HTTP_200_OK, response_model=List[schema.JobOut])
def get_all_jobs(db: Session = Depends(get_db), limit: int=10, skip: int=0, title: str | None = None):
    jobs = db.query(models.Job)

    # apply the filter
    if title:
        jobs = jobs.filter(models.Job.jobTitle.contains(title))
    jobs = jobs.limit(limit).offset(skip).all()    
    return jobs

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_job(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Job).filter(models.Job.id == id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Job Id should be deleted")
    query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schema.Job)
def update_job(id: int, job: schema.JobCreate, db: Session = Depends(get_db)):
    job_update = db.query(models.Job).filter(models.Job.id == id)
    if not job_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job with {id} doesn't exist")
    job_update.update(**job.dict(), synchronize_session=False)
    db.commit()
    return job_update.first()

