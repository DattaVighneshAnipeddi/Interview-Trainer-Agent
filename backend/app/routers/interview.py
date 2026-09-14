from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.evaluation import EvaluationResult
from app.schemas.interview import InterviewQuestionsResponse
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.evaluation_service import evaluate_answer
from app.services.interview_service import generate_interview_questions
from app.services.session_service import (
    create_session,
    get_session,
    submit_answer,
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


# -----------------------------
# Request Models
# -----------------------------

class InterviewRequest(BaseModel):
    role: str


class EvaluationRequest(BaseModel):
    question: str
    answer: str


# -----------------------------
# Generate Interview Questions
# -----------------------------

@router.post(
    "/questions",
    response_model=InterviewQuestionsResponse
)
def generate_questions(request: InterviewRequest):

    try:

        result = generate_interview_questions(request.role)

        return InterviewQuestionsResponse(
            role=request.role,
            questions=result.questions
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview questions: {str(e)}"
        )


# -----------------------------
# Create Interview Session
# -----------------------------

@router.post(
    "/session",
    response_model=CreateSessionResponse
)
def start_session(request: CreateSessionRequest):

    try:

        result = generate_interview_questions(request.role)

        session = create_session(
            role=request.role,
            questions=result.questions
        )

        return CreateSessionResponse(
            session_id=session.session_id,
            role=session.role,
            current_question=session.questions[0],
            total_questions=len(session.questions)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


# -----------------------------
# Submit Interview Answer
# -----------------------------

@router.post(
    "/session/{session_id}/answer",
    response_model=SubmitAnswerResponse
)
def submit_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest
):

    try:

        # Find the interview session
        session = get_session(session_id)

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )

        # Check if interview is already completed
        if session.current_question >= len(session.questions):
            raise HTTPException(
                status_code=400,
                detail="Interview session is already completed"
            )

        # Get the current question
        current_question = session.questions[
            session.current_question
        ]

        # Evaluate the candidate's answer
        evaluation = evaluate_answer(
            current_question,
            request.answer
        )

        # Save answer and evaluation
        # Then move to the next question
        updated_session = submit_answer(
            session_id,
            request.answer,
            evaluation
        )

        # Check if interview is completed
        interview_completed = (
            updated_session.current_question
            >= len(updated_session.questions)
        )

        # Determine the next question
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
            interview_completed=interview_completed
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


# -----------------------------
# Standalone Answer Evaluation
# -----------------------------

@router.post(
    "/evaluate",
    response_model=EvaluationResult
)
def evaluate(request: EvaluationRequest):

    try:

        result = evaluate_answer(
            request.question,
            request.answer
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate answer: {str(e)}"
        )
