from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.interview_service import generate_interview_questions
from app.services.evaluation_service import evaluate_answer
from app.schemas.evaluation import EvaluationResult

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
# Response Models
# -----------------------------

class InterviewResponse(BaseModel):
    role: str
    questions: str


# -----------------------------
# Generate Questions
# -----------------------------

@router.post(
    "/questions",
    response_model=InterviewResponse
)
def generate_questions(request: InterviewRequest):

    try:

        questions = generate_interview_questions(request.role)

        return InterviewResponse(
            role=request.role,
            questions=questions
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview questions: {str(e)}"
        )


# -----------------------------
# Evaluate Answer
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
