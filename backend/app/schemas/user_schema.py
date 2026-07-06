from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
