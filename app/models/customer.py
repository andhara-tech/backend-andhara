# This file contains the models for customers
from pydantic import BaseModel, EmailStr
from typing import Optional


class BaseClient(BaseModel):
    documento_cliente: str
    id_tipo_documento: int
    nombres_cliente: str
    apellidos_cliente: str
    numero_telefono: str
    correo_electronico: EmailStr
    direccion_residencia: str


class CreateClient(BaseClient):
    pass


class ClientUpdate(BaseModel):
    documento_cliente: Optional[str] = None
    id_tipo_documento: Optional[int] = None
    nombres_cliente: Optional[str] = None
    apellidos_cliente: Optional[str] = None
    numero_telefono: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    direccion_residencia: Optional[str] = None


class Customer(BaseClient):
    class Config:
        from_attributes = True
