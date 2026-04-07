from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Root API test
def test_root():
    response = client.get("/")
    assert response.status_code == 200


# Register user test
def test_register():
    response = client.post("/auth/register", json={
        "username": "user_test_1",
        "password": "123456"
    })
    assert response.status_code in [200, 400]


# Login user test
def test_login():
    response = client.post("/auth/login", json={
        "username": "user_test_1",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
