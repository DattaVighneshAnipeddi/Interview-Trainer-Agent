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


class Project(BaseModel):
    title: str
    description: str


class Experience(BaseModel):
    company: str
    role: str
    duration: str


class Resume(BaseModel):
    personal_info: PersonalInfo
    skills: List[str]
    education: Education
    projects: List[Project] = []
    experience: List[Experience] = []
    certifications: List[str] = []
    raw_text: str