# This file contains the models for products into db
from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    product_id: int
    supplier_id: int
    product_name: str
    product_description: str
    purchase_price: float
    product_discount: float
    sale_price: float
    profit_margin: float
    vat: float


class CreateProduct(BaseModel):
    supplier_id: int
    product_name: str
    product_description: str
    purchase_price: float
    product_discount: Optional[float] = 0.0
    sale_price: float
    vat: float = 19.0


class ProductUpdate(BaseModel):
    supplier_id: Optional[int] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    product_discount: Optional[float] = None
    profit_margin: Optional[float] = None
    vat: Optional[float] = None


class Product(ProductBase):
    class Config:
        from_attributes = True
