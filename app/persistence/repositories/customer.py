# This file contains the main logic of repository of customers
from typing import List, Optional
from app.utils.transformers import transform_keys, transform_keys_reverse

from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
)
from app.persistence.db.connection import (
    get_supabase,
)

client_field_map = {
    "documento_cliente": "customer_document",
    "id_tipo_documento": "document_type_id",
    "nombres_cliente": "first_name",
    "apellidos_cliente": "last_name",
    "numero_telefono": "phone_number",
    "correo_electronico": "email",
    "direccion_residencia": "home_address",
} # Check where this data will be managed

class CustomerRepository:
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "customer"

    async def create(
        self, new_customer: CreateClient
    ) -> Customer:
        data = transform_keys_reverse(new_customer.model_dump(), client_field_map)
        response = (
            self.supabase.table(self.table)
            .insert(data)
            .execute()
        )
        return Customer(**transform_keys(response.data[0], client_field_map))

    async def get_by_document(
        self, customer_document: str
    ) -> Optional[Customer]:
        response = (
            self.supabase.table(self.table)
            .select("*")
            .eq(
                "customer_document",
                customer_document,
            )
            .execute()
        )
        if response.data:
            return Customer(**transform_keys(response.data[0], client_field_map))
        return None

<<<<<<< HEAD
=======
    async def inactivate_customer(
        self, customer_document: str
    ) -> bool:
        response = (
            self.supabase.table(self.table)
            .update({"customer_state": False})
            .eq(
                "customer_document",
                customer_document,
            )
            .execute()
        )
        return len(response.data) > 0

>>>>>>> b48f1bd6a4e3a82efaff68c3a916de87c48c2814
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
            Customer(**transform_keys(row, client_field_map))for row in response.data
        ]

    async def update(
        self,
        customer_document: str,
        customer: ClientUpdate,
    ) -> Optional[Customer]:
        data = transform_keys_reverse(
            customer.model_dump(
                exclude_unset=True,
            ),
            client_field_map
        )
        if not data:
            return None

        response = (
            self.supabase.table(self.table)
            .update(data)
            .eq(
                "customer_document",
                customer_document,
            )
            .execute()
        )
        if response.data:
            return Customer(**transform_keys(response.data[0], client_field_map))
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