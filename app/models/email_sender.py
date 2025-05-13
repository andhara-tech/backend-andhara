from datetime import datetime

from pydantic import BaseModel


class Normalized(BaseModel):
    customer_service_status: bool | None
    customer_document: str | None
    customer_name: str | None
    phone_number: str | None
    purchase_duration: str | None
    purchase_date: datetime | None
