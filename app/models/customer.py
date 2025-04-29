from __future__ import annotations

from datetime import date  # noqa: TC003
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr, validator


class DocumentType(str, Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"
    NIT = "NIT"
    PASS = "PASS"  # noqa: S105


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
    next_purchase_date: date | None = None
    total_purchase: float
    products: list[PurchaseProductResponse] = []


class CustomerByDocumentResponse(BaseModel):
    customer_document: constr(min_length=5, max_length=20)
    document_type: DocumentType
    customer_first_name: constr(min_length=1, max_length=100)
    customer_last_name: constr(min_length=1, max_length=100)
    phone_number: constr(min_length=10, max_length=10)
    email: EmailStr
    home_address: str | None = None
    customer_state: bool
    total_historical_purchases: float
    branch: BranchResponse | None = None
    purchases: list[PurchaseResponse]

    class Config:
        from_attributes = True


class Customer(BaseModel):
    customer_document: constr(min_length=5, max_length=20)
    document_type: DocumentType
    customer_first_name: constr(min_length=1, max_length=100)
    customer_last_name: constr(min_length=1, max_length=100)
    phone_number: constr(min_length=10, max_length=10)
    email: EmailStr
    home_address: str | None = None
    customer_state: bool = True
    branch: BranchResponse | None = None
    last_purchase: PurchaseResponse | None = None

    class Config:
        from_attributes = True


class CreateClient(BaseModel):
    customer_document: constr(min_length=5, max_length=20)
    document_type: DocumentType
    customer_first_name: constr(min_length=1, max_length=100)
    customer_last_name: constr(min_length=1, max_length=100)
    phone_number: constr(min_length=10, max_length=10)
    email: EmailStr
    home_address: str | None = None
    customer_state: bool = True
    id_branch: str

    @validator("id_branch")
    def id_branch_must_be_uuid(cls, id_branch: str) -> UUID:  # noqa: N805
        try:
            UUID(id_branch)
            return id_branch
        except ValueError:
            msg = "id_branch must be a valid UUID"
            raise ValueError(msg)  # noqa: B904


class ClientUpdate(BaseModel):
    customer_first_name: constr(min_length=1, max_length=100) | None = None
    customer_last_name: constr(min_length=1, max_length=100) | None = None
    phone_number: constr(min_length=10, max_length=10) | None = None
    email: EmailStr | None = None
    home_address: str | None = None
    customer_state: bool | None = None
    id_branch: str | None = None

    @validator("id_branch")
    def id_branch_must_be_uuid(cls, id_branch: str) -> UUID:  # noqa: N805
        try:
            UUID(id_branch)
            return id_branch
        except ValueError:
            msg = "id_branch must be a valid UUID"
            raise ValueError(msg)  # noqa: B904


class CustomerBasic(BaseModel):
    customer_document: str
    customer_first_name: str
    customer_last_name: str
