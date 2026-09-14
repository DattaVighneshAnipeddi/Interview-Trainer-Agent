from pydantic import BaseModel
from typing import List

from app.schemas.evaluation import EvaluationResult


class InterviewSession(BaseModel):
    session_id: str
    role: str

    questions: List[str]

    current_question: int = 0

    answers: List[str] = []

    evaluations: List[EvaluationResult] = []


class CreateSessionRequest(BaseModel):
    role: str


class CreateSessionResponse(BaseModel):
    session_id: str
    role: str
    current_question: str
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    answer: str


class SubmitAnswerResponse(BaseModel):
    evaluation: EvaluationResult
    next_question: str | None
    remaining_questions: int
    interview_completed: bool
