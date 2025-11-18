from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None
    user_type: str | None = None

class User(BaseModel):
    email: EmailStr
    password: str

class EmployerBase(BaseModel):   
    org_name: str 
    actively_hiring: bool = True

class EmployerCreate(EmployerBase, User):
    """Used for registration (requires email + password) """
    pass

class EmployerOut(EmployerBase):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Job(BaseModel):
    job_title: str
    job_description: str
    experience_start: int
    experience_end: int
    job_location: str
    salary_lower_range: Optional[int] = None
    salary_upper_range: Optional[int] = None 

class JobOut(Job):
    id : int
    created_at: datetime
    employer: EmployerOut

    class Config:
        from_attributes = True

#------------CANDIDATE----------

class CandidateBase(BaseModel):
    name: str
    designation: str
    years_of_exp: int

class CandidateCreate(User, CandidateBase):
    """Used for registration"""
    pass

class CandidateUpdate(CandidateBase):
    """Used for profile updates"""
    name: str
    designation: str
    years_of_exp: int

class CandidateOut(CandidateBase):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobApplicationOut(BaseModel):
    id: int
    job: JobOut
    candidate: CandidateOut

    class Config:
        from_attributes = True

class JobApplicateCreate(BaseModel):
    candidate_id: int
    










