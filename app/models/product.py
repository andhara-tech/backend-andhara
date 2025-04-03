# This file contains the models for products into db
from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    nombre_producto: str
    descripcion_producto: str
    precio_compra: float
    descuento_producto: float
    precio_venta: float
    margen_ganacia: float
    iva: float
