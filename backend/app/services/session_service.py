import uuid

from app.schemas.session import InterviewSession
from app.schemas.evaluation import EvaluationResult


# Temporary in-memory storage
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


def submit_answer(
    session_id: str,
    answer: str,
    evaluation: EvaluationResult
) -> InterviewSession:

    session = sessions.get(session_id)

    if session is None:
        raise ValueError("Interview session not found")

    # Store the candidate's answer
    session.answers.append(answer)

    # Store the AI evaluation
    session.evaluations.append(evaluation)

    # Move to the next question
    session.current_question += 1

    return session
