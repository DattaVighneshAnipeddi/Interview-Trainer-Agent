
import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.services.session_service import create_session


client = TestClient(app)


@pytest.fixture
def ownership_test_db(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_ownership_api.db",
    )
    database.init_db()

    with database.get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO users (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "User One", "one@example.com", "test-hash"),
                (2, "User Two", "two@example.com", "test-hash"),
            ],
        )


@pytest.fixture
def set_authenticated_user():
    original = app.dependency_overrides.copy()

    def authenticate_as(user_id):
        app.dependency_overrides[get_current_user] = lambda: UserResponse(
            user_id=user_id,
            name=f"User {user_id}",
            email=f"user{user_id}@example.com",
            role="user",
        )

    yield authenticate_as

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original)


def test_other_user_cannot_submit_answer_or_view_report(
    ownership_test_db,
    set_authenticated_user,
):
    session = create_session(
        user_id=1,
        role="Python Developer",
        questions=["What is Python?"],
    )

    set_authenticated_user(2)

    answer_response = client.post(
        f"/interview/session/{session.session_id}/answer",
        json={"answer": "Python is a programming language."},
    )
    report_response = client.get(
        f"/interview/session/{session.session_id}/report",
    )

    assert answer_response.status_code == 404, answer_response.text
    assert report_response.status_code == 404, report_response.text
