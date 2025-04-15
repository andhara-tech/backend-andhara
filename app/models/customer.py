# This file contains the models for customers
from pydantic import BaseModel, EmailStr
from typing import Optional


class BaseClient(BaseModel):
    customer_document: str
    document_type_id: int
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr
    home_address: str


class CreateClient(BaseClient):
    pass


class ClientUpdate(BaseModel):
    customer_document: Optional[str] = None
    document_type_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    home_address: Optional[str] = None


class Customer(BaseClient):
    class Config:
        from_attributes = True
