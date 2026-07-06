from fastapi import APIRouter
from app.schemas.user_schema import UserRegister
from app.services.auth_service import register_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(user: UserRegister):
    """
    Register a new user.
    """
    return register_user(
        full_name=user.full_name,
        email=user.email,
        password=user.password
    )
