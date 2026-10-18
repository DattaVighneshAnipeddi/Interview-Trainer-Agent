
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection
from app.schemas.auth import UserResponse
from app.services.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM


bearer_scheme = HTTPBearer(auto_error=False)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired access token.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserResponse:
    """Validate the access token and retrieve its active database user."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UNAUTHORIZED

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        subject = payload["sub"]

        if not isinstance(subject, str) or not subject.isdecimal():
            raise jwt.InvalidTokenError("Invalid subject")

        user_id = int(subject)

        if user_id <= 0:
            raise jwt.InvalidTokenError("Invalid subject")

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise UNAUTHORIZED

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT user_id, name, email, role
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        raise UNAUTHORIZED

    return UserResponse(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
    )
