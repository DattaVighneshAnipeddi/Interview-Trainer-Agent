
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_registration_rejects_whitespace_only_name():
    response = client.post(
        "/auth/register",
        json={
            "name": "   ",
            "email": "validation@example.com",
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == 422


def test_registration_rejects_short_password():
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "shortpass@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_login_rejects_empty_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "",
        },
    )
    assert response.status_code == 422


def test_registration_rejects_invalid_email():
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "not-an-email",
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == 422
