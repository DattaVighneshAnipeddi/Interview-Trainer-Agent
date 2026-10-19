
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.evaluation import EvaluationResult
from app.schemas.interview import InterviewQuestionsResponse
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    InterviewHistoryItem,
)

from app.services.evaluation_service import evaluate_answer
from app.services.interview_service import generate_interview_questions
from app.services.session_service import (
    create_session,
    get_session,
    submit_answer,
    get_user_interview_history,
)
from app.services.report_service import generate_interview_report
from app.services.gemini_service import (
    GeminiQuotaExceeded,
    GeminiServiceUnavailable,
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)


# -----------------------------
# Request Models
# -----------------------------

class InterviewRequest(BaseModel):
    role: str = Field(min_length=1)


class EvaluationRequest(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


# -----------------------------
# Shared Gemini Error Handling
# -----------------------------

def handle_gemini_error(exc: Exception) -> HTTPException:
    """Convert known Gemini service errors into HTTP responses."""

    if isinstance(exc, GeminiQuotaExceeded):
        return HTTPException(status_code=429, detail=str(exc))

    if isinstance(exc, GeminiServiceUnavailable):
        return HTTPException(status_code=503, detail=str(exc))

    return HTTPException(
        status_code=500,
        detail="An unexpected error occurred while processing the request.",
    )


# -----------------------------
# Generate Interview Questions
# -----------------------------

@router.post(
    "/questions",
    response_model=InterviewQuestionsResponse,
)
def generate_questions(
    request: InterviewRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    role = request.role.strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role cannot be empty",
        )

    try:
        result = generate_interview_questions(role)

        return InterviewQuestionsResponse(
            role=role,
            questions=result.questions,
        )

    except (GeminiQuotaExceeded, GeminiServiceUnavailable) as exc:
        raise handle_gemini_error(exc) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate interview questions.",
        ) from exc


# -----------------------------
# Create Interview Session
# -----------------------------

@router.post(
    "/session",
    response_model=CreateSessionResponse,
)
def start_session(
    request: CreateSessionRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    role = request.role.strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role cannot be empty",
        )

    try:
        result = generate_interview_questions(role)

        if not result.questions:
            raise HTTPException(
                status_code=500,
                detail="No interview questions were generated",
            )

        session = create_session(
            user_id=current_user.user_id,
            role=role,
            questions=result.questions,
        )

        return CreateSessionResponse(
            session_id=session.session_id,
            role=session.role,
            current_question=session.questions[0],
            total_questions=len(session.questions),
        )

    except HTTPException:
        raise

    except (GeminiQuotaExceeded, GeminiServiceUnavailable) as exc:
        raise handle_gemini_error(exc) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to create interview session.",
        ) from exc


# -----------------------------
# Submit Interview Answer
# -----------------------------

@router.post(
    "/session/{session_id}/answer",
    response_model=SubmitAnswerResponse,
)
def submit_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    session = get_session(
        session_id,
        current_user.user_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    if session.current_question >= len(session.questions):
        raise HTTPException(
            status_code=400,
            detail="Interview session is already completed",
        )

    answer = request.answer.strip()

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty",
        )

    current_question = session.questions[session.current_question]

    try:
        evaluation = evaluate_answer(
            current_question,
            answer,
        )

        updated_session = submit_answer(
            session_id,
            current_user.user_id,
            answer,
            evaluation,
        )

        interview_completed = (
            updated_session.current_question
            >= len(updated_session.questions)
        )

        if interview_completed:
            next_question = None
            remaining_questions = 0
        else:
            next_question = updated_session.questions[
                updated_session.current_question
            ]
            remaining_questions = (
                len(updated_session.questions)
                - updated_session.current_question
            )

        return SubmitAnswerResponse(
            evaluation=evaluation,
            next_question=next_question,
            remaining_questions=remaining_questions,
            interview_completed=interview_completed,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (GeminiQuotaExceeded, GeminiServiceUnavailable) as exc:
        raise handle_gemini_error(exc) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to submit interview answer.",
        ) from exc


# -----------------------------
# Standalone Answer Evaluation
# -----------------------------

@router.post(
    "/evaluate",
    response_model=EvaluationResult,
)
def evaluate(
    request: EvaluationRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    question = request.question.strip()
    answer = request.answer.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty",
        )

    try:
        return evaluate_answer(
            question,
            answer,
        )

    except (GeminiQuotaExceeded, GeminiServiceUnavailable) as exc:
        raise handle_gemini_error(exc) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate the answer.",
        ) from exc


# -----------------------------
# Final Interview Report
# -----------------------------

@router.get(
    "/session/{session_id}/report",
)
def get_interview_report(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return generate_interview_report(
            session_id,
            current_user.user_id,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Interview session not found":
            status_code = 404
        elif message in (
            "Interview session is not yet completed",
            "No interview responses are available",
        ):
            status_code = 400
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc

    except (GeminiQuotaExceeded, GeminiServiceUnavailable) as exc:
        raise handle_gemini_error(exc) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate interview report.",
        ) from exc


# -----------------------------
# Interview History
# -----------------------------

@router.get(
    "/history",
    response_model=list[InterviewHistoryItem],
)
def get_interview_history(
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return get_user_interview_history(
            current_user.user_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve interview history.",
        ) from exc
