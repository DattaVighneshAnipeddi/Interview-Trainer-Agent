from fastapi import Depends
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from fastapi import APIRouter, HTTPException, status
from sqlite3 import IntegrityError

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    try:
        user = register_user(
            name=request.name.strip(),
            email=str(request.email).lower(),
            password=request.password,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    token = create_access_token(user)

    return TokenResponse(
        access_token=token,
        user=user,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = authenticate_user(
        email=str(request.email),
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user)

    return TokenResponse(
        access_token=token,
        user=user,
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: UserResponse = Depends(get_current_user),
):
    return current_user
