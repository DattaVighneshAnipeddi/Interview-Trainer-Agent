
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.evaluation import EvaluationResult
from app.services.session_service import create_session, submit_answer


TEST_USER_ID = 1
OTHER_USER_ID = 2

client = TestClient(app)


def override_get_current_user():
    return UserResponse(
        user_id=TEST_USER_ID,
        name="Test User",
        email="test@example.com",
        role="user",
    )


app.dependency_overrides[get_current_user] = override_get_current_user


def setup_test_users(tmp_path, monkeypatch):
    """Give each test its own clean SQLite database."""
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_interview_history.db",
    )

    database.init_db()

    with database.get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users
                (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (TEST_USER_ID, "Test User", "test@example.com", "test-hash"),
        )

        connection.execute(
            """
            INSERT INTO users
                (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (OTHER_USER_ID, "Other User", "other@example.com", "test-hash"),
        )


def make_evaluation():
    return EvaluationResult(
        overall_score=8.0,
        technical_accuracy=8.0,
        communication=8.0,
        completeness=8.0,
        strengths="Clear explanation",
        weaknesses="Needs more detail",
        suggestions="Add practical examples",
        improved_answer="A detailed answer.",
    )


def test_empty_interview_history(tmp_path, monkeypatch):
    setup_test_users(tmp_path, monkeypatch)

    response = client.get("/interview/history")

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_history_shows_only_current_users_sessions(
    tmp_path, monkeypatch
):
    setup_test_users(tmp_path, monkeypatch)

    own_session = create_session(
        user_id=TEST_USER_ID,
        role="Python Developer",
        questions=["What is Python?", "What is a decorator?"],
    )

    create_session(
        user_id=OTHER_USER_ID,
        role="Java Developer",
        questions=["What is Java?"],
    )

    response = client.get("/interview/history")

    assert response.status_code == 200, response.text

    history = response.json()

    assert len(history) == 1
    assert history[0]["session_id"] == own_session.session_id
    assert history[0]["role"] == "Python Developer"
    assert history[0]["total_questions"] == 2
    assert history[0]["answered_questions"] == 0
    assert history[0]["status"] == "in_progress"


def test_completed_session_appears_as_completed(
    tmp_path, monkeypatch
):
    setup_test_users(tmp_path, monkeypatch)

    session = create_session(
        user_id=TEST_USER_ID,
        role="Python Developer",
        questions=["What is Python?"],
    )

    submit_answer(
        session.session_id,
        TEST_USER_ID,
        "Python is a programming language.",
        make_evaluation(),
    )

    response = client.get("/interview/history")

    assert response.status_code == 200, response.text

    history = response.json()

    assert len(history) == 1
    assert history[0]["session_id"] == session.session_id
    assert history[0]["answered_questions"] == 1
    assert history[0]["status"] == "completed"

def test_history_is_ordered_by_recently_updated(tmp_path, monkeypatch):
    setup_test_users(tmp_path, monkeypatch)

    older_session = create_session(
        user_id=TEST_USER_ID,
        role="Python Developer",
        questions=["What is Python?"],
    )

    newer_session = create_session(
        user_id=TEST_USER_ID,
        role="Java Developer",
        questions=["What is Java?"],
    )

    # Ensure the second session has a later update timestamp.
    with database.get_connection() as connection:
        connection.execute(
            """
            UPDATE interview_sessions
            SET updated_at = '2099-01-02 10:00:00'
            WHERE session_id = ?
            """,
            (newer_session.session_id,),
        )
        connection.execute(
            """
            UPDATE interview_sessions
            SET updated_at = '2099-01-01 10:00:00'
            WHERE session_id = ?
            """,
            (older_session.session_id,),
        )

    response = client.get("/interview/history")

    assert response.status_code == 200, response.text

    history = response.json()

    assert len(history) == 2
    assert history[0]["session_id"] == newer_session.session_id
    assert history[1]["session_id"] == older_session.session_id


def test_history_requires_authentication():
    # Temporarily remove the test authentication override.
    original_override = app.dependency_overrides.pop(
        get_current_user, None
    )

    try:
        response = client.get("/interview/history")
        assert response.status_code == 401, response.text
    finally:
        # Restore the override so other tests remain unaffected.
        if original_override is not None:
            app.dependency_overrides[
                get_current_user
            ] = original_override
