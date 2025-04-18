# This file contains the main logic of service of products
# It is responsible for the business logic of the products
from typing import List, Optional

from fastapi import HTTPException, status

from app.models.branch_stock import BranchStockUpdate, CreateBranchStock
from app.models.product import (
    CreateProduct,
    Product,
    ProductBase,
    ProductUpdate,
)
from app.persistence.repositories.branch_stock import BranchStockRepository
from app.persistence.repositories.product import ProductRepository

from app.utils.products import (
    calculate_profit_margin,
)

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
        self.stock_repository = BranchStockRepository()

    async def create_product(
        self, product: CreateProduct
    ) -> Product:
        # Calculate the profit margin
        profit_margin = calculate_profit_margin(
            product.purchase_price,
            product.sale_price,
        )
        # Create the product
        created_product = await self.repository.create(
            product, profit_margin
        )
        # Create the stocks
        product_stock = [
            await self.stock_repository.create(
                CreateBranchStock(
                    id_product=created_product.id_product,
                    id_branch=stock.id_branch,
                    quantity=stock.quantity
                )
            )
            for stock in product.stock
        ]
        return Product(**created_product.model_dump(), stock=product_stock)

    async def get_product_by_id(
        self, id_product: str
    ) -> Optional[Product]:
        return await self.repository.get_by_id(
            id_product
        )

    async def list_all_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        return await self.repository.list_all_products(
            skip, limit
        )

    async def update_product(
        self,
        id_product: str,
        product: ProductUpdate,
    ) -> Optional[Product]:
        if product.purchase_price is not None or product.sale_price is not None:
            # Calculate the profit margin if not provided
            profit_margin = (
                calculate_profit_margin(
                    product.purchase_price,
                    product.sale_price,
                )
            )
            product.profit_margin = (
                profit_margin
            )

        if product.stock is not None:
            counter = 0
            # Update the stock for the product
            for stock in product.stock:
                stock_updated = await self.stock_repository.update(
                    id_product, BranchStockUpdate(id_branch=stock.id_branch, quantity=stock.quantity),
                )
                if stock_updated:
                    counter+= 1
            if not counter == len(product.stock):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Al menos uno de los stocks no pudieron ser actualizados."
                )

        return await self.repository.update(
            id_product, product
        )

    async def inactivate_product(
        self, id_product: str
    ) -> bool:
        return await self.repository.inactivate_product(
            id_product
        )
