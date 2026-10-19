
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.evaluation import EvaluationResult
from app.rate_limiter import limiter


@pytest.fixture
def authenticated_client():
    original_overrides = app.dependency_overrides.copy()
    original_limiter_enabled = limiter.enabled

    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        user_id=1,
        name="Test User",
        email="test@example.com",
        role="user",
    )

    limiter.enabled = True
    limiter.reset()

    try:
        with TestClient(app) as client:
            yield client
    finally:
        limiter.reset()
        limiter.enabled = original_limiter_enabled
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_interview_questions_rate_limit(authenticated_client):
    with patch(
        "app.routers.interview.generate_interview_questions"
    ) as mock_generate:
        mock_generate.return_value.questions = [
            "What is Python?",
            "Explain OOP.",
        ]

        payload = {"role": "Python Developer"}

        responses = [
            authenticated_client.post("/interview/questions", json=payload)
            for _ in range(6)
        ]

    assert all(response.status_code == 200 for response in responses[:5])
    assert responses[5].status_code == 429


def test_create_session_rate_limit(authenticated_client):
    with (
        patch(
            "app.routers.interview.generate_interview_questions"
        ) as mock_generate,
        patch(
            "app.routers.interview.create_session"
        ) as mock_create_session,
    ):
        mock_generate.return_value.questions = [
            "What is Python?",
            "Explain OOP.",
        ]

        mock_session = Mock()
        mock_session.session_id = "test-session"
        mock_session.role = "Python Developer"
        mock_session.questions = [
            "What is Python?",
            "Explain OOP.",
        ]
        mock_create_session.return_value = mock_session

        payload = {"role": "Python Developer"}

        responses = [
            authenticated_client.post("/interview/session", json=payload)
            for _ in range(6)
        ]

    assert all(response.status_code == 200 for response in responses[:5])
    assert responses[5].status_code == 429


def test_evaluate_answer_rate_limit(authenticated_client):
    with patch(
        "app.routers.interview.evaluate_answer"
    ) as mock_evaluate:
        mock_evaluate.return_value = EvaluationResult(
            overall_score=8,
            technical_accuracy=8,
            communication=8,
            completeness=8,
            strengths="Clear explanation",
            weaknesses="Could use more detail",
            suggestions="Add a practical example",
            improved_answer=(
                "Python is a versatile, high-level programming language."
            ),
        )

        payload = {
            "question": "What is Python?",
            "answer": "Python is a programming language.",
        }

        responses = [
            authenticated_client.post(
                "/interview/evaluate",
                json=payload,
            )
            for _ in range(11)
        ]

    assert all(response.status_code == 200 for response in responses[:10])
    assert responses[10].status_code == 429


def test_submit_answer_rate_limit(authenticated_client):
    session_id = "test-session"

    mock_session = Mock()
    mock_session.current_question = 0
    mock_session.questions = ["What is Python?"]

    mock_updated_session = Mock()
    mock_updated_session.current_question = 1
    mock_updated_session.questions = ["What is Python?"]

    mock_evaluation = EvaluationResult(
        overall_score=8,
        technical_accuracy=8,
        communication=8,
        completeness=8,
        strengths="Clear explanation",
        weaknesses="Could use more detail",
        suggestions="Add a practical example",
        improved_answer=(
            "Python is a versatile, high-level programming language."
        ),
    )

    with (
        patch(
            "app.routers.interview.get_session",
            return_value=mock_session,
        ),
        patch(
            "app.routers.interview.evaluate_answer",
            return_value=mock_evaluation,
        ),
        patch(
            "app.routers.interview.submit_answer",
            return_value=mock_updated_session,
        ),
    ):
        payload = {
            "answer": "Python is a programming language."
        }

        responses = [
            authenticated_client.post(
                f"/interview/session/{session_id}/answer",
                json=payload,
            )
            for _ in range(11)
        ]

    assert all(response.status_code == 200 for response in responses[:10])
    assert responses[10].status_code == 429
