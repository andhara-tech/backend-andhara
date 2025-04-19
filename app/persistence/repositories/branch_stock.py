# This file contains the main logic of repository of stock in a branch.
# It is responsible for interacting with the database and performing CRUD
from typing import List, Optional

from app.models.branch_stock import (
    CreateBranchStock,
    BranchStockUpdate,
    BranchStock,
)
from app.persistence.db.connection import (
    get_supabase,
)


class BranchStockRepository:
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "branch_stock"

    async def create(
        self,
        stock: CreateBranchStock,
    ) -> BranchStock:
        data = stock.model_dump()
        response = (
            self.supabase.table(self.table)
            .insert(data)
            .execute()
        )
        return BranchStock(**response.data[0])

    async def list_all_stock(
        self, skip: int = 0, limit: int = 100
    ) -> List[BranchStock]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .range(skip, skip + limit)
            .execute()
        )
        if response.data:
            return response.data
        return None

    async def get_stock_by_product_id(
        self,
        id_prodcut,
    ) -> List[BranchStock]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .eq("id_product", id_prodcut)
            .range(0, 5)
            .execute()
        )
        if response.data:
            return response.data
        return None

    async def update(
        self,
        id_product: str,
        stock: BranchStockUpdate,
    ) -> Optional[BranchStock]:
        data = stock.model_dump()

        if not data:
            return None

        response = (
            self.supabase.table(self.table)
            .update(
                {"quantity": data["quantity"]}
            )
            .eq("id_product", id_product)
            .eq("id_branch", data["id_branch"])
            .execute()
        )
        if response.data:
            return BranchStock(**response.data[0])
        return None
