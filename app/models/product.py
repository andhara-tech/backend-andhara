# This file contains the models for products into db
from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    id_producto: int
    id_proveedor: int
    nombre_producto: str
    descripcion_producto: str
    precio_compra: float
    descuento_producto: float
    precio_venta: float
    margen_ganancia: float
    iva: float

class CreateProduct(BaseModel):
    id_proveedor: int
    nombre_producto: str
    descripcion_producto: str
    precio_compra: float
    descuento_producto: Optional[float]= 0.0
    precio_venta: float
    iva: float = 19.0

class ProductUpdate(BaseModel):
    id_proveedor: Optional[int]= None
    nombre_producto: Optional[str]= None
    descripcion_producto: Optional[str]= None
    precio_compra: Optional[float]= None
    precio_venta: Optional[float]= None
    descuento_producto: Optional[float]= None
    margen_ganancia: Optional[float]= None
    iva: Optional[float]= None


class Product(ProductBase):
    class Config:
        from_attributes = True
