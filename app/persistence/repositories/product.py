# This file contains the main logic of repository of products
# It is responsible for interacting with the database and performing CRUD operations
from typing import List, Optional
from app.utils.transformers import transform_keys, transform_keys_reverse

from app.models.product import (
    CreateProduct,
    Product,
    ProductUpdate,
)
from app.persistence.db.connection import (
    get_supabase,
)

product_field_map = {
    "id_producto": "product_id",
    "id_proveedor": "supplier_id",
    "nombre_producto": "product_name",
    "descripcion_producto": "product_description",
    "precio_compra": "purchase_price",
    "descuento_producto": "product_discount",
    "precio_venta": "sale_price",
    "margen_ganancia": "profit_margin",
    "iva": "vat",
} # Check where this data will be managed

class ProductRepository:
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "producto"

    async def create(
        self, new_product: CreateProduct, margen_ganancia: float
    ) -> Product:
        data = transform_keys_reverse(new_product.model_dump(), product_field_map)
        # Add the profit margin to the data
        data["margen_ganancia"] = margen_ganancia
        
        response = (
            self.supabase.table(self.table)
            .insert(data)
            .execute()
        )
        return Product(**transform_keys(response.data[0], product_field_map))

    async def get_by_id(
        self, id_product: int
    ) -> Optional[Product]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .eq(
                "id_producto",
                id_product,
            )
            .execute()
        )
        if response.data:
            return Product(**transform_keys(response.data[0], product_field_map))
        return None

    async def list_all_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .range(skip, skip + limit)
            .execute()
        )

        return [
            Product(**transform_keys(row, product_field_map)) for row in response.data
        ]

    async def update(
        self,
        id_product: int,
        product: ProductUpdate,
    ) -> Optional[Product]:
        data = transform_keys_reverse(product.model_dump(exclude_unset=True), product_field_map)

        if not data:
            return None

        response = (
            self.supabase.table(self.table)
            .update(data)
            .eq(
                "id_producto",
                id_product,
            )
            .execute()
        )
        if response.data:
            return Product(**transform_keys(response.data[0], product_field_map))
        return None


    async def delete_product(
        self, id_product: int
    ) -> bool:
        response = (
            self.supabase.table(self.table)
            .delete()
            .eq(
                "id_producto",
                id_product,
            )
            .execute()
        )
        return len(response.data) > 0
