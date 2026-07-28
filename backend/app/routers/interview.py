from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.evaluation import EvaluationResult
from app.schemas.interview import InterviewQuestionsResponse
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
)
from app.services.evaluation_service import evaluate_answer
from app.services.interview_service import generate_interview_questions
from app.services.session_service import create_session

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


class InterviewRequest(BaseModel):
    role: str


class EvaluationRequest(BaseModel):
    question: str
    answer: str


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
