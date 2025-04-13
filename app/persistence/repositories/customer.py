# This file contains the main logic of repository of customers
from typing import List, Optional

from app.models.customer import (
    CreateClient,
    Customer,
    ClientUpdate,
)
from app.persistence.db.connection import (
    get_supabase,
)


class CustomerRepository:
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "cliente"

    async def create(
        self, customer: CreateClient
    ) -> Customer:
        data = customer.model_dump()
        response = (
            self.supabase.table(self.table)
            .insert(data)
            .execute()
        )
        return Customer(**response.data[0])

    async def get_by_document(
        self, customer_document: str
    ) -> Optional[Customer]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .eq(
                "documento_cliente",
                customer_document,
            )
            .execute()
        )
        if response.data:
            return Customer(**response.data[0])
        return None

    async def delete_customer(
        self, customer_document: str
    ) -> bool:
        response = (
            self.supabase.table(self.table)
            .delete()
            .eq(
                "documento_cliente",
                customer_document,
            )
            .execute()
        )
        return len(response.data) > 0

    async def list_all_customers(
        self, skip: int = 0, limit: int = 100
    ) -> List[Customer]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .range(skip, skip + limit)
            .execute()
        )
        return [
            Customer(**item)
            for item in response.data
        ]

    async def update(
        self,
        customer_document: str,
        customer: ClientUpdate,
    ) -> Optional[Customer]:
        data = customer.model_dump(
            exclude_unset=True
        )
        if not data:
            return None

        response = (
            self.supabase.table(self.table)
            .update(data)
            .eq(
                "documento_cliente",
                customer_document,
            )
            .execute()
        )
        if response.data:
            return Customer(**response.data[0])
        return None
