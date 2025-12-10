from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None
    user_type: str | None = None

class User(BaseModel):
    email: EmailStr
    password: str = Field(min_length = 1)

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
    job_id: int
    candidate: CandidateOut
    application_status: str
    applied_at: datetime

    class Config:
        from_attributes = True
    
class JobApplicationWithDetails(BaseModel):
    id: int
    job_id: int
    applied_at: datetime
    application_status : str
    job: JobOut

    class Config:
        from_attributes = True

class JobApplicants(BaseModel):
    id: int 
    applied_at: datetime
    candidate: CandidateOut
    application_status: str

    class Config:
        from_attributes = True

class ApplicationStatusEnum(str, Enum):
    reviewing = "reviewing"
    accepted = "accepted"
    rejected = "rejected"

class ApplicationStatus(BaseModel):
    application_status: ApplicationStatusEnum

class ApplicationViews(BaseModel):
    views : int







