from typing import Literal

from gotrue import User
from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseUser):
    role: Literal[
        "admin",
        "usuario-bogota",
        "usuario-cali",
    ]


class UserResponse(BaseModel):
    user: User
