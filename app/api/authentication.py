# This file contains the authentication system for the project
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from supabase import Client

from app.persistence.db.connection import get_supabase
from app.models import authentication

# Instance the router
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found, please contact the admin"}},
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
            {"email": user.email, "password": user.password},
        )
        user_data: dict = {"id": response.user.id,
                           "email": response.user.email}
        return JSONResponse(
            status_code=201,
            content={"message": "User created successfully", "user": user_data},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
