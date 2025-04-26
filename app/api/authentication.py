# This file contains the authentication system for the project
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from gotrue import User
from supabase import Client

from app.models.authentication import BaseUser, CreateUser, UserResponse
from app.persistence.db.connection import get_admin_supabase, get_supabase
from app.services.authentication import (
    AuthenticationService,
    is_allowed_user,
    verify_user,
)

# Instance the router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        404: {"description": "Not found, please contact the admin"},
    },
)

# Instance the service class using the singleton pattern
service = AuthenticationService()


# Create a new user
@router.post("/create-user")
async def create_user(
    user: CreateUser,
    supabase: Annotated[Client, Depends(get_admin_supabase)],
    current_user: Annotated[UserResponse, Depends(verify_user)],
) -> JSONResponse:
    """
    Register a new user (Admin Only).

    Creates a new user in the Supabase authentication system.
    This action is **restricted to admin users only**.

    **Requires:**
    - `Bearer token` of an authenticated and authorized user.

    **Request Body:**
    - `email`: Email of the user to create.
    - `password`: Strong password for the account.
    - `role`: Role to assign to the new user (`admin`, `<usuario-sede>`, etc.).

    **Returns:**
    - 201 Created: When the user is successfully created.
    - JSON with user ID and email.

    **Raises:**
    - 401 Unauthorized: If the current user is not allowed to create users.
    - 409 Conflict: If the email is already registered.
    - 400 Bad Request: For other creation errors.
    """
    # Verify if the current user is and admin user
    # If current user is not an admin user the system will raise an error
    if not is_allowed_user(
        current_user.user.email,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{
                current_user.user.email
            }' is not allowed to create new users, please contact the admin",
        )
    # Validate if the user exist previously
    # List all the existing users
    user_list: list[User] = supabase.auth.admin.list_users()
    # Extract only the emails from the current users
    email_list: list[str] = [user.email for user in user_list]
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
            },
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
            detail=f"User creation failed - {e!s}",
        ) from e


# Login exiting users
@router.post("/login")
async def login(
    user: BaseUser,
    supabase: Annotated[Client, Depends(get_supabase)],
) -> JSONResponse:
    """
    Authenticate a user and return an access token.

    This endpoint allows a user to log in using their email and password.
    If the credentials are valid, a JWT access token and basic user info
    are returned.

    - `email`: The user's email.
    - `password`: The user's password.

    **Returns:**
        200 OK with the access token and user info (email, role, user_id).

    **Raises:**
        401 Unauthorized: If the credentials are invalid or login fails.
    """
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password,
            },
        )
        return JSONResponse(
            status_code=200,
            content={
                "token": response.session.access_token,
                "user": {
                    "email": response.user.email,
                    "role": response.user.role,
                    "user_id": response.user.id,
                },
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Loing failed - {e!s}",
        ) from e


@router.delete("/delete-user")
def delete_user(
    user_id: UUID,
    admin_supabase: Annotated[Client, Depends(get_admin_supabase)],
    current_user: Annotated[UserResponse, Depends(verify_user)],
) -> JSONResponse:
    """
    Delete a user from Supabase.

    This endpoint allows an admin user to delete an existing user
    from the Supabase authentication system using the user's UUID.

     - `user_id`: UUID of the user to delete (passed as a query parameter).

    **Returns:**
        200 OK with a success message if deletion is successful.

    **Raises:**
        401 Unauthorized: If the current user does not have permission.
        400 Bad Request: If there is an error deleting the user.
    """
    # Verify if the user is allowed
    if not is_allowed_user(
        current_user.user.email,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{
                current_user.user.email
            }' is not allowed to create new users, please contact the admin",
        )

    try:
        admin_supabase.auth.admin.delete_user(user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"User '{user_id}' has been deleted successfully"
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting user wiht id '{user_id}' - {e!s}",
        ) from e


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_all_users(
    current_user: Annotated[User, Depends(verify_user)],
) -> list[User]:
    """
    List all users from Supabase.

    This endpoint allows an admin user to retrieve a list of all users
    registered in the Supabase authentication system.

    - `current_user`: Currently authenticated user (injected via dependency).

    **Returns:**
        200 OK with a list of all users if the request is successful.

    **Raises:**
        401 Unauthorized: If the current user does not have admin permissions.
        400 Bad Request: If there is an error retrieving the user list.
    """
    try:
        # Verify if the current user is and admin user
        # If current user is not an admin user the system will raise an error
        if not is_allowed_user(current_user.user.email):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User '{
                    current_user.user.email
                }' not allowed to create list users, please contact the admin",
            )
        return await service.list_all_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/logout",
    dependencies=[Depends(verify_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_user(
    authorization: Annotated[str, Header()] = ...,
) -> JSONResponse:
    """
    Log out the currently authenticated user.

    This endpoint invalidates the user's session using Supabase authentication.
    It requires the user to be authenticated.

    **Returns:**
    - None

    **Raises:**
    - HTTPException:
        - `400 Bad Request` if the logout operation fails.
    """
    try:
        # Get the token from the Authorization header
        token = authorization.replace("Bearer ", "")
        # Catch the logout result
        success = await service.logout_user(token=token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User logout failed",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User logout failed - {e!s}",
        ) from e
