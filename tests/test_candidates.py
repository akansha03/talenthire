import pytest
from app import schema
from fastapi import status

@pytest.mark.parametrize("email, password, name, designation, years_of_exp, status", [('candidate1@test.com', 'password', "Candidate", "Architect", 10, status.HTTP_201_CREATED)])
def test_create_a_candidate(client, email, password, name, designation, years_of_exp, status):
    payload = {"email" : email, "password" : password, "name" : name, "designation" : designation, "years_of_exp" : years_of_exp}
    response = client.post("/candidates/me", json=payload)
    new_candidate = schema.CandidateOut(**response.json())
    assert response.status_code == status
    assert new_candidate.email == email
    assert new_candidate.name == name
    assert new_candidate.designation == designation
    assert new_candidate.years_of_exp == years_of_exp

@pytest.mark.parametrize("email, password, name, designation, years_of_exp, status", [('a@test', None, '123', 'ere', 10, status.HTTP_422_UNPROCESSABLE_CONTENT)])
def test_create_an_invalid_candidate(client, email, password, name, designation, years_of_exp, status):
    payload = {"email" : email, "password" : password, "name" : name, "designation" : designation, "years_of_exp" : years_of_exp}
    response = client.post("/candidates/me", json=payload)
    assert response.status_code == status

def test_get_a_candidate(authorized_candidate, test_create_candidate):
    response = authorized_candidate.get("/candidates/me")
    assert response.status_code == status.HTTP_200_OK
    candidate =  schema.CandidateOut(**response.json())
    assert candidate.id == test_create_candidate['id']

def test_unauthorized_get_candidate(client):
    response = client.get("/candidates/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_a_candidate(authorized_candidate):
    response = authorized_candidate.delete("/candidates/me")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_unauthorized_delete_a_candidate(client):
    assert client.delete("/candidates/me").status_code == status.HTTP_401_UNAUTHORIZED

def test_update_a_candiadte(authorized_candidate):
    payload = {"name" : "Akansha", "designation" : "Solutions Engineer", "years_of_exp" : 10}
    response = authorized_candidate.put("/candidates/me", json=payload)
    assert response.status_code == status.HTTP_200_OK

def test_unauthorized_update_a_candiadte(client):
    payload = {"name" : "Akansha", "designation" : "Solutions Engineer", "years_of_exp" : 10}
    response = client.put("/candidates/me", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_my_applications(authorized_candidate, apply_for_job):
    response = authorized_candidate.get("/candidates/me/my-applications")
    applications = response.json()
    assert len(applications) == 1
    assert response.status_code == status.HTTP_200_OK

    application = schema.JobApplicationWithDetails(**applications[0])
    assert application.job_id == apply_for_job['job'].id

    assert application.job.job_title == apply_for_job['job'].job_title
    assert application.job.job_description == apply_for_job['job'].job_description
    assert application.job.experience_start == apply_for_job['job'].experience_start
    assert application.job.experience_end == apply_for_job['job'].experience_end
    assert application.job.job_location == apply_for_job['job'].job_location
    assert application.job.salary_lower_range == apply_for_job['job'].salary_lower_range
    assert application.job.salary_upper_range == apply_for_job['job'].salary_upper_range
   

   