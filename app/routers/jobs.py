from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schema
from typing import List, Optional, Literal
from .. import oauth2
from sqlalchemy import func, desc

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
def get_a_single_job(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'job with id: {id} is not found')
    job.view_count += 1
    db.commit()    
    return job

@router.get("", status_code=status.HTTP_200_OK, response_model=List[schema.JobOut])
def get_all_jobs(
        search: Optional[str] = Query(None, description='Search by title or description'),
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        experience_min: Optional[int] = None,
        experience_max: Optional[int] = None,
        order_by: Optional[str] = Query("created_at", description = "Sort Field"),
        order: Optional[str] = Query("desc", description = "Ascending or Descending"),
        db: Session = Depends(get_db), 
        limit: int=10, 
        skip: int=0
    ):

    jobs = db.query(models.Job)
    if search:
        pattern = f"%{search}%"
        jobs = jobs.filter(models.Job.job_title.ilike(pattern) | models.Job.job_description.ilike(pattern))

    if location:
        jobs = jobs.filter(models.Job.job_location.ilike(f"%{location}%"))    

    if salary_min:
        jobs = jobs.filter(models.Job.salary_lower_range >= salary_min)
    if salary_max:
        jobs = jobs.filter(models.Job.salary_upper_range < salary_max)

    if experience_min: 
        jobs = jobs.filter(models.Job.experience_start >= experience_min)
    if experience_max:
        jobs = jobs.filter(models.Job.experience_end < experience_max)    

    sort_column = getattr(models.Job, order_by, None)
    if sort_column is not None:
        if order == "desc":
            jobs = jobs.order_by(sort_column.desc())
        else:
            jobs = jobs.order_by(sort_column.asc())              


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

@router.patch("/{id}/candidate/{candidate_id}", status_code=status.HTTP_200_OK, response_model=schema.ApplicationStatus)
def update_application_status(
    id: int,
    candidate_id: int,
    applicationStatus: schema.ApplicationStatus,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")

    job_exists = db.query(models.Job).filter(models.Job.id == id).first()
    if not job_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job doesn't exist")   

    candidate_exists = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate doesn't exist")

    job_applied =  (db.query(models.CandidateJobApplication)
        .filter(
            models.CandidateJobApplication.job_id == id, models.CandidateJobApplication.candidate_id == candidate_id))
            
    existing = job_applied.first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No one has applied for this job")
    job_applied.update(applicationStatus.dict(), synchronize_session=False)
    db.commit()
    db.refresh(existing)
    return existing

@router.get("/{id}/views", status_code=status.HTTP_200_OK)
def get_count_views_for_jobs(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id: {id} not found")
    return {"views": job.view_count}

@router.get("/job/most-popular", status_code=status.HTTP_200_OK)
def get_popular_job(db: Session = Depends(get_db)):
    result = (
        db.query(models.CandidateJobApplication.job_id,
            func.count(models.CandidateJobApplication.id).label("jobs"))
            .group_by(models.CandidateJobApplication.job_id)
            .order_by(desc("jobs"))
            .limit(1)
            .first()
    )
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Jobs found")
    job = db.query(models.Job).filter(models.Job.id == result.job_id).first()    
    return {"applied" : result.jobs, "designation": job.job_title}

@router.get("/job/most-viewed", status_code=status.HTTP_200_OK)
def get_most_viewed_job(db: Session = Depends(get_db)):
    result = db.query(models.Job).group_by(models.Job.id).order_by(desc(models.Job.view_count)).limit(1).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Jobs found")

    return {"views" : result.view_count, "job" : result}    

    







    
    



