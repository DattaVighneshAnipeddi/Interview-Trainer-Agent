from pydantic import BaseModel
from typing import List, Optional


class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[str] = None
    graduation_year: Optional[str] = None


class Resume(BaseModel):
    personal_info: PersonalInfo
    skills: List[str]
    education: Education
    raw_text: str
