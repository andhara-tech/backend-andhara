from pydantic import BaseModel, EmailStr, constr
from enum import Enum
from uuid import UUID
from datetime import date
from typing import Optional, List


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
    unit_quantity: int
    subtotal_without_vat: float
    total_price_with_vat: float


class PurchaseResponse(BaseModel):
    id_purchase: UUID
    purchase_date: date
    purchase_duration: int
    next_purchase_date: Optional[date] = (
        None  # Cambiado a Optional
    )
    total_purchase: float
    products: List[PurchaseProductResponse] = []


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
    id_branch: UUID


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
    id_branch: Optional[UUID] = None

