import pytest
from app import schema
from fastapi import status

@pytest.mark.parametrize(
        "job_title, job_description, experience_start, experience_end, job_location, salary_lower_range, salary_upper_range, status_code, view_count, status", 
        [('JT1', 'JD1', 2, 10, 'Mumbai', 12000, 25000, status.HTTP_201_CREATED, 4, "active"), ('JT2', 'JD2', 1, 5, 'Bengaluru', 20000, 30000, status.HTTP_201_CREATED, 5, "expired")])
def test_create_a_job(authorized_employer, test_create_employer, job_title, job_description, experience_start, experience_end, job_location, salary_lower_range, salary_upper_range, status_code, view_count, status):
        payload = {"job_title" : job_title, "job_description" : job_description, "experience_start": experience_start,
                "experience_end" : experience_end, "job_location" : job_location, 
                "salary_lower_range" : salary_lower_range, "salary_upper_range" : salary_upper_range, 
                "view_count" : view_count, "status" : status}
        response = authorized_employer.post("/jobs", json = payload) 
        assert response.status_code == status_code
        new_job = schema.JobOut(**response.json())
        assert new_job.job_title == job_title
        assert new_job.job_description == job_description
        assert new_job.experience_start == experience_start
        assert new_job.experience_end == experience_end
        assert new_job.job_location == job_location
        assert new_job.salary_lower_range == salary_lower_range
        assert new_job.salary_upper_range == salary_upper_range
        assert new_job.employer.id == test_create_employer['id']

@pytest.mark.parametrize(
        "job_title, job_description, experience_start, experience_end, job_location, salary_lower_range, salary_upper_range, status_code", 
        [('', '', None, None, '', None, None, 422), 
        ('JT1', None, None, None, 'JL1', 2, 4, 422),
        (None, None, None, None, None, None, None, 422),
        ('JT1', 'JD1', 'a', 'c', 'jl1', 1, 1, 422)])
def test_create_an_invalid_job(authorized_employer, job_title, job_description, experience_start, experience_end, job_location, salary_lower_range, salary_upper_range, status_code):
        payload = {"job_title" : job_title, "job_description" : job_description, "experience_start": experience_start,
                "experience_end" : experience_end, "job_location" : job_location, 
                "salary_lower_range" : salary_lower_range, "salary_upper_range" : salary_upper_range}
        response = authorized_employer.post("/jobs", json=payload)
        assert response.status_code == status_code

def test_get_all_jobs(client, test_create_jobs):
        response = client.get("/jobs")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        jobs = response.json()
        assert jobs[0]['job_title'] == "Backend Engineer"
        assert jobs[1]['job_title'] == "Frontend Engineer"

def test_get_single_valid_job(authorized_employer, test_create_jobs):
        response = authorized_employer.get(f"/jobs/{test_create_jobs[0].id}")
        job = schema.JobOut(**response.json())
        assert response.status_code == status.HTTP_200_OK
        assert job.job_title == test_create_jobs[0].job_title
        assert job.job_description == test_create_jobs[0].job_description
        assert job.experience_start == test_create_jobs[0].experience_start
        assert job.experience_end == test_create_jobs[0].experience_end
        assert job.job_location == test_create_jobs[0].job_location
        assert job.salary_lower_range == test_create_jobs[0].salary_lower_range
        assert job.salary_upper_range == test_create_jobs[0].salary_upper_range

def test_get_an_invalid_job(authorized_employer):
        response = authorized_employer.get(f"/jobs/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_invalid_format_job(authorized_employer):
        response = authorized_employer.get(f"/jobs/abc")
        assert response.status_code == 422

def test_non_employer_get_a_job(client):
        response = client.get("/jobs/123")
        assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_a_job(authorized_employer, test_create_jobs):
        response = authorized_employer.delete(f"/jobs/{test_create_jobs[0].id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_an_invalid_job(authorized_employer):
        response = authorized_employer.delete('/jobs/123')
        assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_an_invalid_job_format(authorized_employer):
        response = authorized_employer.delete("/jobs/abc")
        assert response.status_code == 422

def test_delete_an_empty_job(authorized_employer):
        response = authorized_employer.delete("/jobs/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED  

def test_unauthorized_delete_a_job(client):
        response = client.delete("/jobs/123")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_a_job_authorized_user(authorized_employer, test_create_jobs):
        data = {
                "job_title": "JT1",
                "job_description" : "JD1",
                "experience_start" : 2,
                "experience_end" : 5,
                "job_location" : "Germany",
                "salary_lower_range" : 20000,
                "salary_upper_range" :  50000
        }

        response = authorized_employer.put(f"/jobs/{test_create_jobs[0].id}", json=data)
        assert response.status_code == 200
        assert test_create_jobs[0].job_title == data['job_title']
        assert test_create_jobs[0].job_description == data['job_description']

def test_update_an_invalid_payload(authorized_employer, test_create_jobs):
        data = {}
        response = authorized_employer.put(f"/jobs/{test_create_jobs[0].id}", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_an_invalid_job(authorized_employer):
        data = {
                "job_title": "JT1",
                "job_description" : "JD1",
                "experience_start" : 2,
                "experience_end" : 5,
                "job_location" : "Germany",
                "salary_lower_range" : 20000,
                "salary_upper_range" : 50000
        }
        response = authorized_employer.put('/jobs/999', json = data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

def test_apply_for_job(authorized_candidate, authorized_employer):
        payload = {
                "job_title": "JT1",
                "job_description": "JD1",
                "experience_start": 2,
                "experience_end": 10,
                "job_location": "Mumbai",
                "salary_lower_range": 12000,
                "salary_upper_range": 25000,
        }
        
        # Employer creates job
        resp = authorized_employer.post("/jobs", json=payload)
        assert resp.status_code == status.HTTP_201_CREATED
        new_job = schema.JobOut(**resp.json())

        # Candidate applies to that job
        candidate_resp = authorized_candidate.post(f"/jobs/{new_job.id}/apply")
        assert candidate_resp.status_code == status.HTTP_200_OK

def test_apply_for_an_invalid_job(authorized_candidate):
        response = authorized_candidate.post('/jobs/123/apply')
        assert response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_apply_a_job(client):
        response = client.post('/jobs/4/apply')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_apply_for_an_invalid_format_job_id(authorized_candidate):
        response = authorized_candidate.post("/jobs/abc/apply")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_job_applicants(authorized_employer, apply_for_job):
        job_id = apply_for_job["job"].id
        response = authorized_employer.get(f"/jobs/{job_id}/applicants")
        assert response.status_code == status.HTTP_200_OK

def test_filter_job_by_title(client, test_create_jobs):
        title = test_create_jobs[0].job_title
        response = client.get(f"/jobs?search={title}")
        jobs = response.json()
        expectedTitle = jobs[0]['job_title']
        assert expectedTitle == title

def test_filter_job_by_description(client, test_create_jobs):
        description = test_create_jobs[0].job_description
        response = client.get(f"/jobs?search={description}")
        jobs = response.json()
        assert jobs[0]['job_description'] == description       

def test_filter_job_by_location(client, test_create_jobs):
        location = test_create_jobs[0].job_location
        response = client.get(f"/jobs?location={location}")
        jobs = response.json()
        assert jobs[0]['job_location'] == location

def test_filter_job_by_experience_lower_range(client, test_create_jobs):
        experience_min = 1
        response = client.get(f"/jobs?experience_min={experience_min}")
        jobs = response.json()
        assert jobs[0]['experience_start'] >= experience_min
        assert jobs[1]['experience_start'] >= experience_min 

def test_filter_job_by_experience_upper_range(client, test_create_jobs):
        experience_max = 10
        response = client.get(f"/jobs?experience_max={experience_max}")
        jobs = response.json()
        assert jobs[0]['experience_end'] < experience_max
        assert jobs[1]['experience_end'] < experience_max 

def test_filter_job_by_salary_lower_range(client, test_create_jobs):
        salary_min = 10000
        response = client.get(f"/jobs?salary_min={salary_min}")
        jobs = response.json()
        assert jobs[0]['salary_lower_range'] >= salary_min
        assert jobs[1]['salary_lower_range'] >= salary_min 

def test_filter_job_by_salary_upper_range(client, test_create_jobs):
        salary_max = 40000
        response = client.get(f"/jobs?salary_max={salary_max}")
        jobs = response.json()
        assert jobs[0]['salary_upper_range'] < salary_max
        assert jobs[1]['salary_upper_range'] < salary_max 

def test_multiple_filters_jobs_no_result(client, test_create_jobs):
        response = client.get("/jobs?search=Engineer&location=India")
        assert len(response.json()) == 0

def test_multiple_filters_jobs(client, test_create_jobs):
        response = client.get("/jobs?search=Engineer&location=Bengaluru&experience_min=1&experience_max=6&salary_max=35000")
        job = response.json()
        assert job[0]['job_location'] == 'Bengaluru'

def test_get_views_per_job(client, test_create_jobs):
        response = client.get(f'/jobs/{test_create_jobs[0].id}/views')
        assert response.status_code == status.HTTP_200_OK
        job_views = schema.ApplicationViews(**response.json())
        assert job_views.view_count == test_create_jobs[0].view_count

def test_update_job_status(authorized_employer, test_create_jobs):
        payload = {"status" : "expired"}
        response = authorized_employer.patch(f'/jobs/{test_create_jobs[0].id}/status', json=payload)
        assert response.status_code == status.HTTP_200_OK
        job_status = schema.JobStatus(**response.json())
        assert job_status.status == payload['status']

def test_unauthorized_update_job_status(client):
        response = client.patch(f'/jobs/123/status')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_invalid_job_status(authorized_employer, test_create_jobs):
        payload = {"status" : "open"}
        response = authorized_employer.patch(f'/jobs/{test_create_jobs[0].id}/status', json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_trendy_job(client, test_create_jobs):
        response = client.get("/jobs/job/trendy")
        assert response.status_code == status.HTTP_200_OK
        job = schema.JobOut(**response.json())
        assert job.job_title == test_create_jobs[1].job_title

def test_get_popular_job(client, apply_for_job):
        response = client.get("/jobs/job/popular")
        assert response.status_code == status.HTTP_200_OK
        job = schema.JobOut(**response.json())
        assert job.job_location == apply_for_job['job'].job_location

