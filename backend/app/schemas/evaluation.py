from pydantic import BaseModel


class EvaluationResult(BaseModel):
    overall_score: float
    technical_accuracy: int
    communication: int
    completeness: int
    strengths: str
    weaknesses: str
    suggestions: str
    improved_answer: str
