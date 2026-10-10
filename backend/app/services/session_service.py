from app.schemas.evaluation import EvaluationResult
from app.schemas.session import (
    InterviewSession,
    InterviewResponse,
)
import uuid


# Temporary in-memory storage
sessions: dict[str, InterviewSession] = {}


def create_session(
    role: str,
    questions: list[str]
) -> InterviewSession:

    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        role=role,
        questions=questions,
    )

    sessions[session.session_id] = session

    return session


def get_session(
    session_id: str
) -> InterviewSession | None:

    return sessions.get(session_id)


def submit_answer(
    session_id: str,
    answer: str,
    evaluation: EvaluationResult
) -> InterviewSession:

    session = sessions.get(session_id)

    if session is None:
        raise ValueError("Interview session not found")

    # Prevent answers after the interview is completed
    if session.current_question >= len(session.questions):
        raise ValueError("Interview session is already completed")

    # Get the question being answered
    question = session.questions[session.current_question]

    # Store the question, answer, and evaluation together
    response = InterviewResponse(
        question=question,
        answer=answer,
        evaluation=evaluation,
    )

    session.responses.append(response)

    # Move to the next question
    session.current_question += 1

    return session
