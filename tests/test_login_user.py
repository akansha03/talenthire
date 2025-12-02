import pytest
from app import schema
from jose import jwt
from app.config import settings


@pytest.mark.parametrize('user_fixture', [('test_create_employer'), ('test_create_candidate')])
def test_user_login(user_fixture, client, request):

    user = request.getfixturevalue(user_fixture)
    response = client.post("/login", data = {"username" : user['email'], "password" : user['password']})
    login_res = schema.Token(**response.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])

    id = payload.get("user_id")
    assert id == user['id']
    assert login_res.token_type == "bearer"
    assert response.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [('akansha@gmail.com', 'password', 403), ('akansha@yahoo.in', None, 403)])
def test_invalid_login(email, password, status_code, client):
    response = client.post("/login", data = {"username" : email, "password" : password})
    assert response.status_code == status_code
