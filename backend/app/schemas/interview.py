from pydantic import BaseModel


class InterviewQuestions(BaseModel):
    questions: list[str]


class InterviewQuestionsResponse(BaseModel):
    role: str
    questions: list[str]
