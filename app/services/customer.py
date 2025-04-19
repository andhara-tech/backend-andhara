from typing import List

from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
)
from app.persistence.repositories.customer import (
    CustomerRepository,
)


class CustomerService:
    def __init__(self):
        self.repository = CustomerRepository()

    async def create_customer(
        self, customer: CreateClient
    ) -> Customer:
        return (
            await self.repository.create_customer(
                customer
            )
        )

    async def get_customer_by_document(
        self, document: str
    ) -> Customer:
        customer = await self.repository.get_customer_by_document(
            document
        )
        if not customer:
            raise Exception(
                f"Customer with document '{document}' not found"
            )
        return customer

    async def inactivate_customer(
        self, document: str
    ) -> bool:
        return await self.repository.inactivate_customer(
            document
        )

    async def list_all_customers(
        self, skip: int, limit: int
    ) -> List[Customer]:
        return await self.repository.list_all_customers(
            skip, limit
        )

    async def update_customer(
        self,
        document: str,
        customer: ClientUpdate,
    ) -> Customer:
        updated_customer = (
            await self.repository.update_customer(
                document, customer
            )
        )
        if not updated_customer:
            raise Exception(
                f"Customer with document '{document}' not found"
            )
        return updated_customer
