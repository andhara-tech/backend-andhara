# This file contains the authentication system for the project
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
)
from fastapi.responses import JSONResponse

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


# Create a new user
@router.post("/signup")
async def signup(
    user: authentication.BaseUser,
    supabase: Client = Depends(get_supabase),
):
    """
    Only the new user needs an email and strong password to be registered
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
            status_code=400, detail=str(e)
        )


@router.post("/login")
async def login(
    user: authentication.BaseUser,
    supabase: Client = Depends(get_supabase),
):
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
            status_code=401, detail=f"{str(e)}"
        )


async def get_current_user(
    request: Request,
    supabase: Client = Depends(get_supabase),
):
    # Get the header of the request
    auth_header = request.headers.get(
        "Authorization"
    )
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="There is no token gave",
        )
    try:
        # Split to get the token without counting the token type "Bearer"
        token = (
            auth_header.split(" ")[1]
            if " " in auth_header
            else auth_header
        )

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
