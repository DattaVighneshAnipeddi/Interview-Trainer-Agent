
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    overall_score: float = Field(ge=0, le=10)
    technical_accuracy: int = Field(ge=0, le=10)
    communication: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    strengths: str = Field(min_length=1)
    weaknesses: str = Field(min_length=1)
    suggestions: str = Field(min_length=1)
    improved_answer: str = Field(min_length=1)
