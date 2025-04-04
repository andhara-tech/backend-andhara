# This file contains the authentication system for the project
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from supabase import Client

from app.persistence.db.connection import (
    get_supabase,
)
from app.models import authentication

# Instance the router
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {
            "description": "Not found, please contact the admin"
        }
    },
)

security = HTTPBearer()


async def verify_user(
    supabase: Client = Depends(get_supabase),
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> Any:
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


# Create a new user
@router.post("/signup")
async def signup(
    user: authentication.BaseUser,
    supabase: Client = Depends(get_supabase),
    current_user: Any = Depends(verify_user),
):
    """
    Register a new user (only for authenticated users).

       🔒 Requires:
       - `Authorization: Bearer <token>` header.

       📥 Request Body:
       - `email`: User's email.
       - `password`: Strong password.
    """
    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
            }
        )
        user_data: dict = {
            "id": response.user.id,
            "email": response.user.email,
        }
        return JSONResponse(
            status_code=201,
            content={
                "message": "User created successfully",
                "user": user_data,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User creation failed - {str(e)}",
        )


# Login exiting users
@router.post("/login")
async def login(
    user: authentication.BaseUser,
    supabase: Client = Depends(get_supabase),
):
    """
    Login for existing users

       📥 Request Body:
       - `email`: User's email.
       - `password`: Strong password.
    """
    try:
        response = (
            supabase.auth.sign_in_with_password(
                {
                    "email": user.email,
                    "password": user.password,
                }
            )
        )
        return JSONResponse(
            status_code=200,
            content={
                "token": response.session.access_token,
                "user": {
                    "email": response.user.email,
                    "role": response.user.role,
                },
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Loing failed - {str(e)}",
        )
