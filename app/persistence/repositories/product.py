# This file contains the main logic of repository of products
# It is responsible for interacting with the database and performing CRUD
from typing import List, Optional
from app.utils.transformers import transform_keys, transform_keys_reverse

from app.models.product import (
    CreateProduct,
    Product,
    ProductBase,
    ProductUpdate,
)
from app.persistence.db.connection import (
    get_supabase,
)
from app.persistence.repositories.branch_stock import BranchStockRepository


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
        self.stock_repository = BranchStockRepository()
        self.table = "product"

    async def create(
<<<<<<< HEAD
        self, new_product: CreateProduct, margen_ganancia: float
    ) -> Product:
        data = transform_keys_reverse(new_product.model_dump(), product_field_map)
        # Add the profit margin to the data
        data["margen_ganancia"] = margen_ganancia
        
=======
        self,
        product: CreateProduct,
        profit_margin: float,
    ) -> ProductBase:
        data = product.model_dump()
        # Add the profit margin to the data and delete the stock entry
        data["profit_margin"] = profit_margin
        del data["stock"]
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814
        response = (
            self.supabase.table(self.table)
            .insert(data)
            .execute()
        )
<<<<<<< HEAD
        return Product(**transform_keys(response.data[0], product_field_map))
=======
        return ProductBase(**response.data[0])
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814

    async def get_by_id(
        self, id_product: str
    ) -> Optional[Product]:
        response = (
            self.supabase.table(self.table)
            .select("*, branch_stock(*)")
            .eq(
                "id_product",
                id_product,
            )
            .execute()
        )
        if response.data:
<<<<<<< HEAD
            return Product(**transform_keys(response.data[0], product_field_map))
=======
            # Change the label of the branch_stock to stock, to be consistent with the Model
            product_data = {**response.data[0], "stock": response.data[0].get("branch_stock", [])}
            return Product(**product_data)
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814
        return None

    async def list_all_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        response = (
            self.supabase.table(self.table)
            .select("*, branch_stock(*)")
            .range(skip, skip + limit)
            .execute()
        )
<<<<<<< HEAD

        return [
            Product(**transform_keys(row, product_field_map)) for row in response.data
        ]
=======
        products = []
        for item in response.data:
            product_data = {
                **item,
                'stock': item.get('branch_stock', [])  # Renaming branch_stock to stock
            }
            products.append(Product(**product_data))
        return products
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814

    async def update(
        self,
        id_product: int,
        product: ProductUpdate,
    ) -> Optional[Product]:
<<<<<<< HEAD
        data = transform_keys_reverse(
            product.model_dump(
                exclude_unset=True
            ),
            product_field_map)
=======
        data = product.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        # Remove the stock entry from the data to avoid errors in the update
        data.pop("stock", None)
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814

        if not data:
            return None

        response = (
            self.supabase.table(self.table)
            .update(data)
            .eq(
                "id_product",
                id_product,
            )
            .execute()
        )
        if response.data:
<<<<<<< HEAD
            return Product(**transform_keys(response.data[0], product_field_map))
=======
            # get and add the stock data to the product updated
            stock = await self.stock_repository.get_stock_by_product_id(id_product)
            return Product(**{**response.data[0], "stock": stock})
>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814
        return None

    async def inactivate_product(
        self, id_product: str
    ) -> bool:
        response = (
            self.supabase.table(self.table)
            .update({"product_state": False})
            .eq(
                "id_product",
                id_product,
            )
            .execute()
        )
        return len(response.data) > 0
