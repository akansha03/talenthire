from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Employer(Base):
    __tablename__ = "employer"

    id = Column(Integer, primary_key=True, nullable=False)
    org_name = Column(String, nullable=False)
    active_hiring = Column(Boolean, server_default='True', nullable=False)
    job_list = relationship("Job")


class Candidate(Base):
    __tablename__="jobseekers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    yearsOfExp = Column(Integer, nullable=False)
    

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, nullable=False)
    designation = Column(String, nullable=False)
    experienceStartRange = Column(Integer, nullable=False)
    experienceEndRange = Column(Integer, nullable=False)
    jobDescription = Column(String, nullable=False)
    applied_to_job = Column(Boolean, nullable=False)
    candidate_id = Column(Integer, ForeignKey("jobseekers.id", ondelete="CASCADE"), primary_key=True)
    employer_id = Column(Integer, ForeignKey("employer.id", ondelete="CASCADE"), primary_key=True)

