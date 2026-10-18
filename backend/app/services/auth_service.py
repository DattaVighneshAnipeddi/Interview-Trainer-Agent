import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

from app.schemas.auth import UserResponse
from app.database import get_connection


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if JWT_ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be greater than zero"
    )

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from the .env file")

password_hash = PasswordHash.recommended()


def register_user(name: str, email: str, password: str) -> UserResponse:
    """Create a user account with a securely hashed password."""
    hashed_password = password_hash.hash(password)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name, email.lower(), hashed_password),
        )

        user_id = cursor.lastrowid

        return UserResponse(
            user_id=user_id,
            name=name,
            email=email.lower(),
            role="user",
        )


def authenticate_user(email: str, password: str) -> UserResponse | None:
    """Verify credentials and return the user if they are valid."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT user_id, name, email, password_hash, role
            FROM users
            WHERE email = ?
            """,
            (email.lower(),),
        ).fetchone()

    if row is None:
        return None

    if not password_hash.verify(password, row["password_hash"]):
        return None

    return UserResponse(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
    )


def create_access_token(user: UserResponse) -> str:
    """Generate a signed JWT access token for the authenticated user."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
