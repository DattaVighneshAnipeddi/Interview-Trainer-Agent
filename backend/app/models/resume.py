from pydantic import BaseModel


class ResumeInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
