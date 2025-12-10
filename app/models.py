from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func
from typing import List


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    actively_hiring = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Candidate(Base):
    __tablename__="candidates"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    years_of_exp = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(String, nullable=False)
    experience_start = Column(Integer, nullable=False)
    experience_end = Column(Integer, nullable=False)
    job_location = Column(String, nullable=False)
    view_count = Column(BigInteger, default=0)
    salary_lower_range = Column(Integer, nullable=False)
    salary_upper_range = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employer_id = Column(Integer, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    employer = relationship("Employer")

class CandidateJobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate")
    job = relationship("Job")
    application_status = Column(String, default='In Review')
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    