
import json
import uuid

from app.database import get_connection
from app.schemas.evaluation import EvaluationResult
from app.schemas.session import InterviewSession, InterviewResponse


def _session_from_row(row) -> InterviewSession:
    """Convert a database row into an InterviewSession."""
    return InterviewSession(
        session_id=row["session_id"],
        user_id=row["user_id"],
        role=row["role"],
        questions=json.loads(row["questions_json"]),
        current_question=row["current_question"],
        responses=[
            InterviewResponse.model_validate(response)
            for response in json.loads(row["responses_json"])
        ],
    )


def _save_new_session(session: InterviewSession) -> None:
    """Insert a new session without allowing an existing session to be overwritten."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO interview_sessions (
                session_id,
                user_id,
                role,
                questions_json,
                current_question,
                responses_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.session_id,
                session.user_id,
                session.role,
                json.dumps(session.questions),
                session.current_question,
                json.dumps(
                    [response.model_dump() for response in session.responses]
                ),
            ),
        )


def _update_session(session: InterviewSession, user_id: int) -> None:
    """Update a session only when it belongs to the specified user."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE interview_sessions
            SET role = ?,
                questions_json = ?,
                current_question = ?,
                responses_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND user_id = ?
            """,
            (
                session.role,
                json.dumps(session.questions),
                session.current_question,
                json.dumps(
                    [response.model_dump() for response in session.responses]
                ),
                session.session_id,
                user_id,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError("Interview session not found")


def create_session(
    user_id: int,
    role: str,
    questions: list[str],
) -> InterviewSession:
    """Create a new interview session owned by a user."""
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        role=role,
        questions=questions,
    )

    _save_new_session(session)
    return session


def get_session(
    session_id: str,
    user_id: int,
) -> InterviewSession | None:
    """Retrieve a session only if it belongs to the requesting user."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT session_id, user_id, role, questions_json,
                   current_question, responses_json
            FROM interview_sessions
            WHERE session_id = ? AND user_id = ?
            """,
            (session_id, user_id),
        ).fetchone()

    if row is None:
        return None

    return _session_from_row(row)


def submit_answer(
    session_id: str,
    user_id: int,
    answer: str,
    evaluation: EvaluationResult,
) -> InterviewSession:
    """Submit an answer only to a session owned by the user."""
    session = get_session(session_id, user_id)

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

    # Enforce ownership again in the database UPDATE.
    _update_session(session, user_id)

    return session


def get_user_interview_history(
    user_id: int,
) -> list[dict]:
    """Return interview history belonging only to the specified user."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                session_id,
                role,
                questions_json,
                current_question,
                created_at,
                updated_at
            FROM interview_sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC, created_at DESC
            """,
            (user_id,),
        ).fetchall()

    history = []

    for row in rows:
        total_questions = len(json.loads(row["questions_json"]))
        answered_questions = row["current_question"]

        history.append(
            {
                "session_id": row["session_id"],
                "role": row["role"],
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "status": (
                    "completed"
                    if answered_questions >= total_questions
                    else "in_progress"
                ),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        )

    return history
