
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, get_connection
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.evaluation import EvaluationResult


TEST_USER_ID = 1

client = TestClient(app)


def override_get_current_user():
    return UserResponse(
        user_id=TEST_USER_ID,
        name="Test User",
        email="test@example.com",
        role="user",
    )


app.dependency_overrides[get_current_user] = override_get_current_user


def ensure_test_user():
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO users
                (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (TEST_USER_ID, "Test User", "test@example.com", "test-hash"),
        )


def make_evaluation(score: float) -> EvaluationResult:
    return EvaluationResult(
        overall_score=score,
        technical_accuracy=score,
        communication=score,
        completeness=score,
        strengths="Explained the concept clearly",
        weaknesses="Could provide another example",
        suggestions="Practise explaining with examples",
        improved_answer="A clearer, more complete example answer.",
    )


def test_complete_interview_workflow():
    ensure_test_user()

    questions = [
        "What is Python?",
        "What is a REST API?",
    ]

    with (
        patch(
            "app.routers.interview.generate_interview_questions"
        ) as mock_questions,
        patch(
            "app.routers.interview.evaluate_answer"
        ) as mock_evaluate,
    ):
        mock_questions.return_value.questions = questions
        mock_evaluate.side_effect = [
            make_evaluation(8.0),
            make_evaluation(10.0),
        ]

        # 1. Create a session.
        response = client.post(
            "/interview/session",
            json={"role": "Python Developer"},
        )

        assert response.status_code == 200, response.text

        session_data = response.json()
        session_id = session_data["session_id"]

        assert session_data["role"] == "Python Developer"
        assert session_data["current_question"] == questions[0]
        assert session_data["total_questions"] == 2

        # 2. Submit the first answer.
        response = client.post(
            f"/interview/session/{session_id}/answer",
            json={
                "answer": "Python is a high-level programming language."
            },
        )

        assert response.status_code == 200, response.text

        first_answer = response.json()

        assert first_answer["interview_completed"] is False
        assert first_answer["next_question"] == questions[1]
        assert first_answer["remaining_questions"] == 1

        # 3. Submit the second and final answer.
        response = client.post(
            f"/interview/session/{session_id}/answer",
            json={
                "answer": "A REST API allows systems to communicate over HTTP."
            },
        )

        assert response.status_code == 200, response.text

        final_answer = response.json()

        assert final_answer["interview_completed"] is True
        assert final_answer["next_question"] is None
        assert final_answer["remaining_questions"] == 0

        # 4. Retrieve the completed interview report.
        response = client.get(
            f"/interview/session/{session_id}/report"
        )

        assert response.status_code == 200, response.text

        report = response.json()

        assert report["session_id"] == session_id
        assert report["role"] == "Python Developer"
        assert report["total_questions"] == 2
        assert report["answered_questions"] == 2
        assert report["overall_score"] == 9.0
        assert len(report["question_reports"]) == 2

        # Two answers should have been evaluated.
        assert mock_evaluate.call_count == 2

    print("PASS: Session creation and question progression.")
    print("PASS: Both answers evaluated and stored.")
    print("PASS: Final report generated with correct average score.")


if __name__ == "__main__":
    test_complete_interview_workflow()
    print("\nInterview workflow test passed!")
