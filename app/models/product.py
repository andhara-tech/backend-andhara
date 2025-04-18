# This file contains the models for products into db
from pydantic import BaseModel
from typing import Optional

from app.models.branch_stock import (
    BranchStock,
    BranchStockUpdate,
    ProductStockEntry
)

class ProductBase(BaseModel):
    id_product: str
    id_supplier: str
    product_name: str
    product_description: str
    purchase_price: float
    product_discount: float
    sale_price: float
    profit_margin: float
    product_state: bool
    vat: float


class CreateProduct(BaseModel):
    id_supplier: str
    product_name: str
    product_description: str
    purchase_price: float
    product_discount: Optional[float] = 0.0
    sale_price: float
    vat: float = 19.0
    product_state: Optional[bool] = True 
    stock: list[ProductStockEntry]


class ProductUpdate(BaseModel):
    id_supplier: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    product_discount: Optional[float] = None
    profit_margin: Optional[float] = None
    product_state: Optional[bool] = None 
    vat: Optional[float] = None
    stock: Optional[list[BranchStockUpdate]] = None


class Product(ProductBase):
    stock: list[BranchStock]
    class Config:
        from_attributes = True
