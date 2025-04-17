# This file contains the models for customers
from pydantic import BaseModel, EmailStr
from typing import Optional


class BaseClient(BaseModel):
    customer_document: str
    document_type: str
    customer_first_name: str
    customer_last_name: str
    phone_number: str
    email: EmailStr
    home_address: str


class CreateClient(BaseClient):
    pass


class ClientUpdate(BaseModel):
    customer_document: Optional[str] = None
    document_type: Optional[str] = None
    customer_first_name: Optional[str] = None
    customer_last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    home_address: Optional[str] = None


class Customer(BaseClient):
    class Config:
        from_attributes = True
