from pydantic import BaseModel



class QuestionReport(BaseModel):
    question: str
    answer: str
    score: float
    technical_accuracy: int
    communication: int
    completeness: int
    strengths: str
    weaknesses: str
    suggestions: str


class InterviewReport(BaseModel):
    session_id: str
    role: str
    total_questions: int
    answered_questions: int
    overall_score: float
    average_technical_accuracy: float
    average_communication: float
    average_completeness: float
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    question_reports: list[QuestionReport]


