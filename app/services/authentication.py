# This file contiains the main for authentication
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import EmailStr
from supabase import Client

from app.core.config import settings
from app.models.authentication import UserResponse
from app.persistence.db.connection import (
    get_supabase,
)
from app.persistence.repositories.authentication import (
    AuthenticationRepository,
)

security = HTTPBearer()


# Function to validate if the user is allowed to make modification on db
def is_allowed_user(
    current_user_email: EmailStr,
) -> bool:
    is_allowed_user: bool = (
        current_user_email == settings.email_admin
    )
    return is_allowed_user


async def verify_user(
    supabase: Client = Depends(get_supabase),
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> UserResponse:
    """
    Verifies the JWT token in the Authorization header.

    - Checks if the token is valid using Supabase Auth.
    - Returns the authenticated user.
    - Raises `HTTP 401` if invalid.
    """
    # Get the Authorization header
    token = credentials.credentials

    try:
        # Verify the user in supabase
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token user not authenticated",
            )

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials - {str(e)}",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


class AuthenticationService:
    def __init__(self):
        self.repository = (
            AuthenticationRepository()
        )

    async def list_all_users(self):
        return (
            await self.repository.list_all_users()
        )
