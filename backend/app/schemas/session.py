from app.schemas.evaluation import EvaluationResult
from pydantic import BaseModel, Field


class InterviewResponse(BaseModel):
    question: str
    answer: str
    evaluation: EvaluationResult


class InterviewSession(BaseModel):
    session_id: str
    user_id: int
    role: str
    questions: list[str]
    current_question: int = 0
    responses: list[InterviewResponse] = Field(default_factory=list)


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
