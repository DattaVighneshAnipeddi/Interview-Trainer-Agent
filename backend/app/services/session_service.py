import uuid

from app.schemas.session import InterviewSession
from app.schemas.evaluation import EvaluationResult


sessions: dict[str, InterviewSession] = {}


def create_session(role: str, questions: list[str]) -> InterviewSession:

    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        role=role,
        questions=questions,
    )

    sessions[session.session_id] = session

    return session


def get_session(session_id: str) -> InterviewSession | None:
    return sessions.get(session_id)
