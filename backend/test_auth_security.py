
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth_dependencies import get_current_user
from app.services.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


def make_token(payload):
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_protected_me_endpoint_rejects_missing_token():
    response = client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    [
        "not-a-valid-token",
        make_token({
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }),
        make_token({
            "email": "test@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }),
        make_token({
            "sub": "invalid",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }),
    ],
)
def test_protected_me_endpoint_rejects_invalid_tokens(token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
