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

class Employer(User):
    org_name: str
    actively_hiring: bool = True

class EmployerCreate(Employer):
    pass
   
class EmployerOut(Employer):
    id: int
    org_name: str
    email: EmailStr
    actively_hiring: bool
    created_at: datetime

    class Config:
        orm_mode = True
    
class Job(BaseModel):
    job_title: str
    job_description: str
    experience_start: int
    experience_end: int
    job_location: str

class JobCreate(Job):
    pass

class JobOut(Job):
    id : int
    created_at: datetime

    class Config:
        orm_mode = True





