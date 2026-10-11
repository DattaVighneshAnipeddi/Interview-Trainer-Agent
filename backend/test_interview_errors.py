
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.evaluation import EvaluationResult
from app.services.session_service import (
    create_session,
    submit_answer,
)

client = TestClient(app)


def make_evaluation():
    return EvaluationResult(
        overall_score=8.0,
        technical_accuracy=8.0,
        communication=8.0,
        completeness=8.0,
        strengths="Clear explanation",
        weaknesses="Needs more detail",
        suggestions="Add practical examples",
        improved_answer="A more detailed example answer.",
    )


def test_answer_for_unknown_session():
    response = client.post(
        "/interview/session/unknown-session/answer",
        json={"answer": "My answer"},
    )

    assert response.status_code == 404
    print("PASS: Unknown session answer returns HTTP 404.")


def test_report_for_unknown_session():
    response = client.get(
        "/interview/session/unknown-session/report"
    )

    assert response.status_code == 404
    print("PASS: Unknown session report returns HTTP 404.")


def test_report_before_interview_completion():
    session = create_session(
        role="Python Developer",
        questions=["What is Python?", "What is a REST API?"],
    )

    response = client.get(
        f"/interview/session/{session.session_id}/report"
    )

    assert response.status_code == 400
    print("PASS: Incomplete interview report returns HTTP 400.")


def test_answer_after_interview_completion():
    session = create_session(
        role="Python Developer",
        questions=["What is Python?"],
    )

    submit_answer(
        session.session_id,
        "Python is a programming language.",
        make_evaluation(),
    )

    response = client.post(
        f"/interview/session/{session.session_id}/answer",
        json={"answer": "Another answer"},
    )

    assert response.status_code == 400
    print("PASS: Answer after completion returns HTTP 400.")


if __name__ == "__main__":
    test_answer_for_unknown_session()
    test_report_for_unknown_session()
    test_report_before_interview_completion()
    test_answer_after_interview_completion()

    print("\nAll interview error tests passed!")
