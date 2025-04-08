from typing import Literal
from pydantic import BaseModel, EmailStr
from gotrue import User


class BaseUser(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseUser):
    role: Literal[
        "admin", "usuario-bogota", "usuario-cali"
    ]


class UserResponse(BaseModel):
    user: User
