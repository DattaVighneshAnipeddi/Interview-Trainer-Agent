
import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from app.auth_dependencies import get_current_user

client = TestClient(app)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_auth.db",
    )
    database.init_db()
    yield


@pytest.fixture(autouse=True)
def clear_auth_override():
    original = app.dependency_overrides.copy()
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original)


def registration_payload(email="test@example.com"):
    return {
        "name": "Test User",
        "email": email,
        "password": "TestPassword123!",
    }


def test_register_success(test_db):
    response = client.post(
        "/auth/register",
        json=registration_payload(),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "test@example.com"


def test_duplicate_registration_returns_conflict(test_db):
    payload = registration_payload()

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201, first.text
    assert second.status_code == 409, second.text


def test_login_success(test_db):
    payload = registration_payload()
    client.post("/auth/register", json=payload)

    response = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["access_token"]


def test_login_wrong_password_returns_401(test_db):
    payload = registration_payload()
    client.post("/auth/register", json=payload)

    response = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401(test_db):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 401
