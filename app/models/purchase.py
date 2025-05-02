"""Module for purchase model."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import UUID4, BaseModel, validator


# Enums basados en el esquema SQL
class PaymentStatus(str, Enum):
    PAGO_PENDIENTE = "Pago Pendiente"
    PAGO_COMPLETADO = "Pago Completado"
    EN_PROCESO = "En Proceso"


class DeliveryType(str, Enum):
    RECOGER_EN_SEDE = "Recoger en Sede"
    DOMICILIO_BOGOTA = "Domicilio Bogotá"
    SERVIENTREGA = "Servientrega"
    RAPPI = "Rappi"
    OTRO = "Otro"


class DeliveryStatus(str, Enum):
    SIN_PREPARAR = "Sin Preparar"
    LISTO_PARA_ENVIO = "Listo para Envío"
    EN_PROCESO = "En Proceso"
    ENTREGADO = "Entregado"


# Modelo para un producto en la venta
class ProductInSale(BaseModel):
    id_product: UUID4
    unit_quantity: int

    @validator("unit_quantity")
    def quantity_must_be_positive(cls, v) -> int:  # noqa: N805
        if v <= 0:
            error_mgs = "The quantity must be greater than 0"
            raise ValueError(error_mgs)
        return v


# Modelo para crear una venta
class SaleCreate(BaseModel):
    customer_document: str
    id_branch: UUID4
    purchase_duration: int  # Duración en días para calcular next_purchase_date
    products: list[ProductInSale]
    payment_type: str
    payment_status: PaymentStatus = PaymentStatus.PAGO_COMPLETADO
    remaining_balance: float = 0.0
    delivery_type: DeliveryType | None = None
    delivery_cost: float = 0.0
    delivery_comment: str | None = None

    @validator("purchase_duration")
    def duration_must_be_non_negative(cls, v) -> int:  # noqa: N805
        if v < 0:
            error_mgs = "The duration must be a non-negative number"
            raise ValueError(error_mgs)
        return v


# Modelos para la respuesta
class ProductInPurchaseResponse(BaseModel):
    id_product: UUID4
    unit_quantity: int
    subtotal_without_vat: float
    total_price_with_vat: float


class PaymentResponse(BaseModel):
    id_payment: UUID4
    id_purchase: UUID4
    payment_type: str
    payment_status: PaymentStatus
    remaining_balance: float


class DeliveryResponse(BaseModel):
    id_delivery: UUID4
    id_purchase: UUID4
    delivery_type: DeliveryType
    delivery_status: DeliveryStatus
    delivery_cost: float
    delivery_comment: str | None


class PurchaseResponse(BaseModel):
    id_purchase: UUID4
    customer_document: str
    purchase_date: date
    purchase_duration: int
    next_purchase_date: date
    products: list[ProductInPurchaseResponse]
    payment: PaymentResponse
    delivery: DeliveryResponse | None
