
# Customer Service Models
from typing import Optional, List
from datetime import date

from pydantic import UUID4, BaseModel, computed_field, Field

from app.models.customer import PurchaseByCustomerDocumentResponse
from app.models.purchase import ProductInPurchaseResponse

# --- Auxiliary Models / Base ---
class BranchBase(BaseModel):
    branch_name: str

class CustomerBase(BaseModel):
    customer_first_name: str
    customer_last_name: str
    phone_number: str
    id_branch: Optional[UUID4] = None

class CustomerNestedInPurchase(CustomerBase): # Specific Model to be used nested in Purchase
    branch: BranchBase

class PurchaseBase(BaseModel):
    customer_document: str

# --- Business Logic Customer Service Models / Supabase ---

class PurchaseInCustomerService(PurchaseBase):
    customer: CustomerNestedInPurchase

# Modelo principal para CustomerService (como viene de Supabase)
class CustomerServiceDB(BaseModel):
    id_customer_service: UUID4
    id_purchase: UUID4
    service_date: date
    next_contact_date: date
    contact_comment: Optional[str] = None
    customer_service_status: bool
    purchase: PurchaseInCustomerService # Nested Model

    class Config:
        orm_mode = True

class CreateCustomerServiceDB(BaseModel):
    id_purchase: UUID4
    service_date: date
    next_contact_date: date
    customer_service_status: bool = True

    class Config:
        orm_mode = True

# --- Service Logic and API Response Models ---

class CustomerServiceCustomerInfo(BaseModel):
    customer_document: str
    customer_first_name: str
    customer_last_name : str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    home_address: Optional[str] = None
    branch_name: str

    class Config:
        orm_mode = True

class CustomerDetail(CustomerServiceCustomerInfo):
    @computed_field
    @property
    def customer_full_name(self) -> str:
        return f"{self.customer_first_name} {self.customer_last_name}"

    class Config:
        orm_mode = True

class CustomerServicePurchase(BaseModel):
    id_purchase: UUID4
    next_contact_date: date
    purchase_date: date
    payment_type: str
    payment_status: str
    products: List[ProductInPurchaseResponse]

    class Config:
        orm_mode = True

# Model for response of endpoint list-all
class CustomerServiceForTable(BaseModel):
    id_customer_service: UUID4
    id_purchase: UUID4
    service_date: date
    customer_full_name: str
    phone_number: Optional[str] = None
    branch_name: str
    days_remaining: Optional[int] = None
    isComment: bool
    contact_comment: Optional[str] = None
    customer_service_status: bool
    id_branch: UUID4

    class Config:
        orm_mode = True

# Model for manage customer service endpoint (PATCH)
class ManageCustomerServicePayload(BaseModel):
    contact_comment: str = Field(..., min_length=1) # Make sure is not an empty string
    customer_service_status: bool = True

# Purchase model for customer service detail 
class PurchaseDetailForService(BaseModel):
    id_purchase: UUID4
    purchase_date: date
    payment_type: str
    payment_status: str
    subtotal_without_vat: float
    total: float
    days_remaining: int

    class Config:
        orm_mode = True

# Main model for customer service detail
class CustomerServiceDetailResponse(BaseModel):
    id_customer_service: UUID4
    customer: CustomerDetail
    purchase: PurchaseDetailForService
    last_purchases: PurchaseByCustomerDocumentResponse

    class Config:
        orm_mode = True
