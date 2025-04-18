# This file contains the models for branch_stock into db
from pydantic import BaseModel
from typing import Optional

class BranchStockBase(BaseModel):
    id_product: str
    id_branch: str
    quantity: int

class CreateBranchStock(BranchStockBase):
    pass

class BranchStockUpdate(BaseModel):
    id_branch: str
    quantity: int
    
# Model for the array of stock when creating a product
class ProductStockEntry (BaseModel):
    id_branch: str
    quantity: int = 0

class BranchStock(BranchStockBase):
    class Config:
        from_attributes = True
