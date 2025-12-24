from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schema, oauth2
from typing import List, Optional, Literal
from sqlalchemy import func, desc
from ..cache import generate_cache_key, set_to_cache, get_from_cache, invalidate_cache

router = APIRouter(prefix="/jobs", tags=['Jobs'])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.JobOut)
def create_a_job(job: schema.Job, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Only employer can create a job")

    new_job = models.Job(employer_id=current_user.id, **job.dict())
    
    if new_job.experience_end <= new_job.experience_start:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="experience start should be less than experience end - Wrong range")
    
    check_for_duplicate_job_entry = db.query(models.Job).filter(models.Job.job_title.contains(new_job.job_title), (models.Job.experience_start == new_job.experience_start) , (models.Job.experience_end == new_job.experience_end), models.Employer.id == current_user.id)
    
    if check_for_duplicate_job_entry.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Job for position {new_job.job_title} already exists') 
    
    db.add(new_job)
    db.commit()
    invalidate_cache("jobs:list:*")
    db.refresh(new_job) 
    return new_job

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def get_a_single_job(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id: {id} doesn't exist")
    job.view_count += 1
    db.commit()    
    return job

"""This function will return the list of jobs after applying a filter 
* search - list of jobs with a matching text as search in title or description.
* location - list of jobs with a matching location
"""
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
        job_status: Optional[str] = None,
        db: Session = Depends(get_db), 
        limit: int=10, 
        skip: int=0
    ):

    cache_key = generate_cache_key(
        "jobs:list",
        search=search,
        location=location,
        salary_min=salary_min,
        salary_max=salary_max,
        experience_min=experience_min,
        experience_max=experience_max,
        order_by=order_by,
        order=order,
        job_status=job_status,
        limit=limit,
        skip=skip
    )

    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result

    jobs = db.query(models.Job)
    if search:
        pattern = f"%{search}%"
        jobs = jobs.filter(models.Job.job_title.ilike(pattern) | models.Job.job_description.ilike(pattern))

    if location:
        jobs = jobs.filter(models.Job.job_location.ilike(f'%{location}%'))    

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

    if job_status:
        jobs = jobs.filter(models.Job.status == job_status)

    jobs = jobs.limit(limit).offset(skip).all()    

    # Convert to dict for caching (SQLAlchemy objects need serialization)
    jobs_dict = [schema.JobOut.from_orm(job).dict() for job in jobs]

    # Remove SQLAlchemy internal attributes
    for job_dict in jobs_dict:
        job_dict.pop('_sa_instance_state', None)

    # Cache for 3 minutes
    set_to_cache(cache_key, jobs_dict, ttl=180)    
    return jobs

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_job(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Job Id : {id} doesnot exist')

    db.delete(job)
    db.commit()
    invalidate_cache("jobs:list:*")
    invalidate_cache("jobs:popular")

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def update_job(id: int, job: schema.Job, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    updated_job = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id)
    if updated_job.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job Id : {id} doesn't exist")
    updated_job.update(job.dict(), synchronize_session=False)
    db.commit()
    invalidate_cache("jobs:list:*")
    invalidate_cache("jobs:popular")
    return updated_job.first()


@router.post("/{id}/apply", status_code=status.HTTP_200_OK, response_model=schema.JobApplicationOut)
def apply_for_a_job(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # Check if the current user is candidate or not
    if not isinstance(current_user, models.Candidate):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")

    # check if the job id exists or not
    job_exist = db.query(models.Job).filter(models.Job.id == id).first()
    if not job_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job with id: {id} doesn't exist")
    
    duplicate_entry = db.query(models.CandidateJobApplication).filter(models.CandidateJobApplication.candidate_id == current_user.id, models.CandidateJobApplication.job_id == id).first()
    if duplicate_entry:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidate has already applied for the job")
    
    application = models.CandidateJobApplication(job_id=id, candidate_id=current_user.id)
    db.add(application) 
    db.commit()
    
    invalidate_cache("jobs:popular")
    db.refresh(application)
    return application

@router.get("/{id}/applicants", status_code=status.HTTP_200_OK, response_model=List[schema.JobApplicants])
def get_job_applicants(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")
    
    # Check whether the job exists or not
    job_exists = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id).first()
    if not job_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job with id: {id} doesn't exist")
    
    applicants = db.query(models.CandidateJobApplication).filter(models.CandidateJobApplication.job_id == id).all()
    if not applicants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No one has applied for this job so far')
    return applicants

@router.patch("/{id}/candidate/{candidate_id}", status_code=status.HTTP_200_OK, response_model=schema.ApplicationStatus)
def update_application_status(
    id: int,
    candidate_id: int,
    applicationStatus: schema.ApplicationStatus,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):

    if not isinstance(current_user, models.Employer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this operation")

    job_exists = db.query(models.Job).filter(models.Job.id == id, models.Job.employer_id == current_user.id).first()
    if not job_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job with id: {id} doesn't exist")   

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

@router.get("/{id}/views", status_code=status.HTTP_200_OK, response_model=schema.ApplicationViews)
def get_count_views_for_jobs(id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id: {id} doesn't exist")
    return job

'''This function will return the popular job, i.e., the job applied by most of the candidates.'''
@router.get("/job/popular", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def get_popular_job(db: Session = Depends(get_db)):

    cache_key = "jobs:popular"

    # Check if the result is cached or not
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result

    # Cache miss - query database 
    result = (
        db.query(models.CandidateJobApplication.job_id,
            func.count(models.CandidateJobApplication.id).label("jobs"))
            .group_by(models.CandidateJobApplication.job_id)
            .order_by(desc("jobs"))
            .limit(1)
            .first()
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Jobs found")
    job = db.query(models.Job).filter(models.Job.id == result.job_id).first()    

    job_dict = schema.JobOut.from_orm(job).dict()
    job_dict.pop('_sa_instance_state', None)
    set_to_cache(cache_key, job_dict, ttl=420)
    return job

'''The function will return the most trendy job, i.e., most viewed by the candidates.'''
@router.get("/job/trendy", status_code=status.HTTP_200_OK, response_model=schema.JobOut)
def get_most_viewed_job(db: Session = Depends(get_db)):
    cache_key = "jobs:trendy"

    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    job = db.query(models.Job).group_by(models.Job.id).order_by(desc(models.Job.view_count)).limit(1).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Jobs found")

    job_dict = schema.JobOut.from_orm(job).dict()
    job_dict.pop('_sa_instance_state', None)
    set_to_cache(cache_key, job_dict, ttl=420)    
    return job


@router.patch("/{id}/status", status_code=status.HTTP_200_OK, response_model=schema.JobStatus)
def update_job_status(id: int, payload: schema.JobStatus, 
                    db: Session = Depends(get_db), 
                    current_user : int = Depends(oauth2.get_current_user)
    ):

    job = db.query(models.Job).filter(models.Job.id == id)
    existing = job.first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job with id: {id} doesn't exist")

    job.update(payload.dict(), synchronize_session=False)
    db.commit()
    db.refresh(existing)
    return existing









    
    



