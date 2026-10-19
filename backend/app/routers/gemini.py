from fastapi import APIRouter, Depends

from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.services.gemini_service import ask_gemini

router = APIRouter(prefix="/gemini", tags=["Gemini"])


@router.get("/test")
def test_gemini(
    current_user: UserResponse = Depends(get_current_user),
):
    response = ask_gemini("Say hello in one sentence.")

    return {
        "response": response
    }
