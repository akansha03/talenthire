import pytest
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.main import app
from fastapi.testclient import TestClient
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def override_get_db_factory(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    #app.dependency_overrides[get_db] = override_get_db
    #yield TestClient(app)
    return override_get_db

# Create an employer
@pytest.fixture
def test_create_employer(session):

    app.dependency_overrides[get_db] = override_get_db_factory(session)
    client = TestClient(app)
    employer_data = {"email" : "amazon@outlook.com", "password": "password", "org_name": "Amazon", "actively_hiring": True}
    response = client.post("/employers/", json=employer_data)
    assert response.status_code == 201

    new_employer = response.json()
    new_employer['password'] = employer_data['password']
    return new_employer

# Create a candidate 
@pytest.fixture
def test_create_candidate(session):
    app.dependency_overrides[get_db] = override_get_db_factory(session)
    client = TestClient(app)
    candidate_data = {"email" : "john@doe.com","password" : "password" ,"name" : "John Doe", "designation" : "Artist", "years_of_exp" : 12}
    response = client.post("/candidates/me", json=candidate_data)
    assert response.status_code == 201

    new_candidate = response.json()
    new_candidate['email'] = candidate_data['email']
    new_candidate['password'] = candidate_data['password']
    new_candidate['name'] = candidate_data['name']
    new_candidate['designation'] = candidate_data['designation']
    return new_candidate

@pytest.fixture
def employer_token(test_create_employer):
    return create_access_token({
        "user_id": test_create_employer['id'], 
        "user_type" : "employer"
    })

@pytest.fixture
def authorized_employer(session, employer_token):
    app.dependency_overrides[get_db] = override_get_db_factory(session)
    client = TestClient(app)
    client.headers['Authorization'] = f'Bearer {employer_token}'
    return client

@pytest.fixture
def authorized_candidate(session, test_create_candidate):
    token = create_access_token({
        "user_id" : test_create_candidate['id'], 
        "user_type" : "candidate"
    })
    app.dependency_overrides[get_db] = override_get_db_factory(session)
    client = TestClient(app) 
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest.fixture
def test_create_jobs(test_create_employer, session, authorized_employer):

    jobs_data = [
        {
            "job_title": "Backend Engineer",
            "job_description": "Python FastAPI",
            "experience_start": 2,
            "experience_end": 5,
            "job_location": "Mumbai",
            "salary_lower_range": 12000,
            "salary_upper_range": 25000
        },
        {
            "job_title": "Frontend Engineer",
            "job_description": "React Developer",
            "experience_start": 1,
            "experience_end": 3,
            "job_location": "Bengaluru",
            "salary_lower_range": 20000,
            "salary_upper_range": 30000
        }
    ]

    def create_job(job):
        return models.Job(employer_id=test_create_employer['id'], **job)

    jobs = list(map(create_job, jobs_data))
    session.add_all(jobs)
    session.commit()
    return jobs    

@pytest.fixture
def apply_for_job(test_create_candidate, session, test_create_employer):

    job = models.Job(
        employer_id = test_create_employer['id'],
        job_title = "Backend Engineer",
        job_description = "Python FastAPI",
        experience_start = 2,
        experience_end = 5,
        job_location = "Mumbai",
        salary_lower_range = 12000,
        salary_upper_range = 25000
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    # Create job application
    application = models.CandidateJobApplication(
        job_id = job.id,
        candidate_id = test_create_candidate['id']      
    )

    session.add(application)
    session.commit()
    session.refresh(application)
    return {"job" : job, "application" : application}

