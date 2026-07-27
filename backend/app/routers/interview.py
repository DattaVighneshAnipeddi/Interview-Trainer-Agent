from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.interview_service import generate_interview_questions

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


class InterviewRequest(BaseModel):
    role: str


class InterviewResponse(BaseModel):
    role: str
    questions: list[str]


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
