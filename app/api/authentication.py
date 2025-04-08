# This file contains the authentication system for the project
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from gotrue import User
from supabase import Client

from app.core.config import settings
from app.models import authentication
from app.persistence.db.connection import (
    get_admin_supabase,
    get_supabase,
)

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
) -> authentication.UserResponse:
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
@router.post("/create-user")
async def create_user(
    user: authentication.CreateUser,
    supabase: Client = Depends(
        get_admin_supabase
    ),
    current_user: authentication.UserResponse = Depends(
        verify_user
    ),
):
    """
    Register a new user (only for authenticated users).

       🔒 Requires:
       - `Authorization: Bearer <token>` header.

       📥 Request Body:
       - `email`: User's email.
       - `password`: Strong password.
       - `role`: What kind of user it is.
    """
    # Verify if the current user is and admin user
    # If current user is not an admin user the system will raise an error
    email_current_user: str = (
        current_user.user.email
    )
    is_allowed_user: bool = (
        email_current_user == settings.email_admin
    )
    if not is_allowed_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{
                email_current_user
            }' is not allowed to create new users, please contact the admin",
        )
    # Validate if the user exist
    # List all the users
    user_list: List[User] = (
        supabase.auth.admin.list_users()
    )
    # Extract only the emails from the current users
    email_list: List[str] = [
        user.email for user in user_list
    ]
    if user.email in email_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"It looks like '{
                user.email
            }' is already registered. Try logging in?",
        )
    try:
        response = supabase.auth.admin.create_user(
            {
                "email": user.email,
                "password": user.password,
                "email_confirm": True,  # Auto confirm the email
                "role": user.role,
            }
        )
        user_data: dict = {
            "id": response.user.id,
            "email": response.user.email,
        }
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
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
