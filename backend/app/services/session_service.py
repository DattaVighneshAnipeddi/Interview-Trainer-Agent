
import json
import uuid

from app.database import get_connection
from app.schemas.evaluation import EvaluationResult
from app.schemas.session import InterviewSession, InterviewResponse


def _save_session(session: InterviewSession) -> None:
    """Insert or update an interview session in SQLite."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO interview_sessions (
                session_id,
                role,
                questions_json,
                current_question,
                responses_json
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                role = excluded.role,
                questions_json = excluded.questions_json,
                current_question = excluded.current_question,
                responses_json = excluded.responses_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                session.session_id,
                session.role,
                json.dumps(session.questions),
                session.current_question,
                json.dumps(
                    [response.model_dump() for response in session.responses]
                ),
            ),
        )


def create_session(
    role: str,
    questions: list[str],
) -> InterviewSession:
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        role=role,
        questions=questions,
    )

    _save_session(session)
    return session


def get_session(session_id: str) -> InterviewSession | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT session_id, role, questions_json,
                   current_question, responses_json
            FROM interview_sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    if row is None:
        return None

    return InterviewSession(
        session_id=row["session_id"],
        role=row["role"],
        questions=json.loads(row["questions_json"]),
        current_question=row["current_question"],
        responses=[
            InterviewResponse.model_validate(response)
            for response in json.loads(row["responses_json"])
        ],
    )


def submit_answer(
    session_id: str,
    answer: str,
    evaluation: EvaluationResult,
) -> InterviewSession:
    session = get_session(session_id)

    if session is None:
        raise ValueError("Interview session not found")

    if session.current_question >= len(session.questions):
        raise ValueError("Interview session is already completed")

    question = session.questions[session.current_question]

    session.responses.append(
        InterviewResponse(
            question=question,
            answer=answer,
            evaluation=evaluation,
        )
    )

    session.current_question += 1
    _save_session(session)

    return session
