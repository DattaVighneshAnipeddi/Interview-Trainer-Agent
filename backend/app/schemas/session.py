from app.schemas.evaluation import EvaluationResult
from pydantic import BaseModel, Field, field_validator


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
    role: str = Field(min_length=2, max_length=100)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError(
                "Role must contain at least 2 non-whitespace characters.")
        return value


class CreateSessionResponse(BaseModel):
    session_id: str
    role: str
    current_question: str
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Answer cannot be empty or whitespace only.")
        return value


class SubmitAnswerResponse(BaseModel):
    evaluation: EvaluationResult
    next_question: str | None
    remaining_questions: int
    interview_completed: bool


class InterviewHistoryItem(BaseModel):
    session_id: str
    role: str
    total_questions: int
    answered_questions: int
    status: str
    created_at: str
    updated_at: str
