# This file contains the main logic of service of products
# It is responsible for the business logic of the products
from typing import List, Optional

from app.models.product import (
    CreateProduct,
    Product,
    ProductUpdate,
)
from app.persistence.repositories.product import (
    ProductRepository,
)
from app.utils.products import (
    calculate_profit_margin,
)


class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    async def create_product(
        self, product: CreateProduct
    ) -> Product:
        # Calculate the profit margin
        margen_ganancia = calculate_profit_margin(
            product.precio_compra,
            product.precio_venta,
        )
        return await self.repository.create(
            product, margen_ganancia
        )

    async def get_product_by_id(
        self, id_product: int
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
        id_product: int,
        product: ProductUpdate,
    ) -> Optional[Product]:
        if product.margen_ganancia is None:
            # Calculate the profit margin if not provided
            margen_ganancia = (
                calculate_profit_margin(
                    product.precio_compra,
                    product.precio_venta,
                )
            )
            product.margen_ganancia = (
                margen_ganancia
            )
        return await self.repository.update(
            id_product, product
        )

    async def inactivate_product(
        self, id_product: int
    ) -> bool:
        return await self.repository.inactivate_product(
            id_product
        )
