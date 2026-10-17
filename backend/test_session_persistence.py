
import app.database as database
from app.schemas.evaluation import EvaluationResult
from app.services import session_service
from app.services.report_service import generate_interview_report


def make_evaluation(score: float) -> EvaluationResult:
    return EvaluationResult(
        overall_score=score,
        technical_accuracy=int(score),
        communication=int(score),
        completeness=int(score),
        strengths="Clear explanation",
        weaknesses="Could provide another example",
        suggestions="Practise with examples",
        improved_answer="A clear, complete answer.",
    )


def create_test_user():
    """Create the test user required by the foreign-key constraint."""
    with database.get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (user_id, name, email, password_hash)
            VALUES (1, 'Test User', 'test@example.com', 'test-hash')
            """
        )


def test_session_and_answers_persist_in_sqlite(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_interview.db",
    )
    database.init_db()
    create_test_user()

    session = session_service.create_session(
        user_id=1,
        role="Python Developer",
        questions=["What is Python?", "What is a decorator?"],
    )

    session_service.submit_answer(
        session.session_id,
        1,
        "Python is a high-level programming language.",
        make_evaluation(8.0),
    )

    # Retrieve the session through a fresh database connection.
    restored = session_service.get_session(session.session_id, 1)

    assert restored is not None
    assert restored.role == "Python Developer"
    assert restored.user_id == 1
    assert restored.current_question == 1
    assert len(restored.responses) == 1
    assert restored.responses[0].evaluation.overall_score == 8.0


def test_completed_session_generates_report_from_sqlite(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_report.db",
    )
    database.init_db()
    create_test_user()

    session = session_service.create_session(
        user_id=1,
        role="Python Developer",
        questions=["What is Python?", "What is a REST API?"],
    )

    session_service.submit_answer(
        session.session_id,
        1,
        "Python is a programming language.",
        make_evaluation(8.0),
    )
    session_service.submit_answer(
        session.session_id,
        1,
        "A REST API enables communication over HTTP.",
        make_evaluation(10.0),
    )

    # The report service reloads the completed session from SQLite.
    report = generate_interview_report(session.session_id, 1)

    assert report.session_id == session.session_id
    assert report.role == "Python Developer"
    assert report.total_questions == 2
    assert report.answered_questions == 2
    assert report.overall_score == 9.0
    assert len(report.question_reports) == 2
