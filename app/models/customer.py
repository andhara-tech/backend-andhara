# This file contains the models for customers
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from enum import Enum
from uuid import UUID
from datetime import date


class DocumentType(str, Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"
    NIT = "NIT"
    PASS = "PASS"


class BranchResponse(BaseModel):
    id_branch: UUID
    branch_name: str
    manager_name: str
    branch_address: str
    city_name: str
    department_name: str


class PurchaseProductResponse(BaseModel):
    id_product: UUID
    product_name: str
    unit_cuantity: int
    subẗotal_without_vat: float
    total_price_without_vat: float


class PurchaseResponse(BaseModel):
    id_purchase: UUID
    purchase_date: str
    purchase_duration: int
    nex_purchase_date: date
    total_purchase: float
    products: list[PurchaseProductResponse] = []


class Customer(BaseModel):
    customer_document: constr(
        min_length=5, max_length=20
    )
    document_type: DocumentType
    customer_first_name: constr(
        min_length=1, max_length=100
    )
    customer_last_name: constr(
        min_length=1, max_length=100
    )
    phone_number: constr(
        min_length=10, max_length=10
    )
    email: EmailStr
    home_address: Optional[str] = None
    customer_state: bool = True
    branch: Optional[BranchResponse] = None
    last_purchase: Optional[PurchaseResponse] = (
        None
    )

    class Config:
        from_attributes = True


class CreateClient(BaseModel):
    customer_document: constr(
        min_length=5, max_length=20
    )
    document_type: DocumentType
    customer_first_name: constr(
        min_length=1, max_length=100
    )
    customer_last_name: constr(
        min_length=1, max_length=100
    )
    phone_number: constr(
        min_length=10, max_length=10
    )
    email: EmailStr
    home_address: Optional[str] = None
    customer_state: bool = True
    id_branch: UUID  # Requerido, ya que ahora customer está vinculado a branch


class ClientUpdate(BaseModel):
    customer_first_name: Optional[
        constr(min_length=1, max_length=100)
    ] = None
    customer_last_name: Optional[
        constr(min_length=1, max_length=100)
    ] = None
    phone_number: Optional[
        constr(min_length=10, max_length=10)
    ] = None
    email: Optional[EmailStr] = None
    home_address: Optional[str] = None
    customer_state: Optional[bool] = None
    id_branch: Optional[UUID] = (
        None  # Permitir actualizar la sede
    )
