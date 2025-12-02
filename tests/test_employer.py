import pytest
from app import schema
from fastapi import status

@pytest.mark.parametrize(
        "email, password, org_name, actively_hiring", 
        [
            ('abc@company.com', 'password', 'company', True),
            ('xyz@company.com', 'password', 'company', False),
            ('def@amazon.com', 'password', 'amazon', True),
        ]
)
def test_create_an_employer(client, email, password, org_name, actively_hiring):
    payload = {"email" : email, "password" : password, "org_name" : org_name, "actively_hiring" : actively_hiring}
    response = client.post("/employers", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    new_employer = schema.EmployerOut(**response.json())
    assert new_employer.email == payload['email']

@pytest.mark.parametrize(
        "email, password, org_name, actively_hiring, status_code",
        [
            ('xyz@company.com', None, 'company', True, status.HTTP_422_UNPROCESSABLE_CONTENT)
        ]
)
def test_create_invalid_employer(client, email, password, org_name, actively_hiring, status_code):
    payload = {"email" : email, "password" : password, "org_name" : org_name, "actively_hiring" : actively_hiring}
    response = client.post("/employers", json=payload)
    assert response.status_code == status_code

@pytest.mark.parametrize(
        "email, password, org_name, actively_hiring", 
        [
            ("abc@company.com", "password", "company", True)
        ]
    )
def test_create_duplicate_employer(client, email, password, org_name, actively_hiring):
    payload = {"email": email, "password": password, "org_name": org_name, "actively_hiring": actively_hiring}
    response = client.post("/employers", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/employers", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT






