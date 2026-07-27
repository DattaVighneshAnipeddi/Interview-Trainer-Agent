from fastapi import APIRouter
from pydantic import BaseModel

from app.services.interview_service import generate_interview_questions

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


class InterviewRequest(BaseModel):
    role: str


@router.post("/questions")
def generate_questions(request: InterviewRequest):
    questions = generate_interview_questions(request.role)

    return {
        "role": request.role,
        "questions": questions
    }