from fastapi import APIRouter
from app.services.gemini_service import ask_gemini

router = APIRouter(prefix="/gemini", tags=["Gemini"])


@router.get("/test")
def test_gemini():
    response = ask_gemini("Say hello in one sentence.")

    return {
        "response": response
    }
