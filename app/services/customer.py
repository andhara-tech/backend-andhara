from typing import List, Optional

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
        # Verify if the customer already exists
        existing_customer = (
            await self.repository.get_by_document(
                customer.customer_document
            )
        )
        if existing_customer:
            raise ValueError(
                "The current customer already exists in database"
            )
        return await self.repository.create(
            customer
        )

    async def get_customer_by_document(
        self, document: str
    ) -> Optional[Customer]:
        return (
            await self.repository.get_by_document(
                document
            )
        )

    async def inactivate_customer(
        self, customer_document: str
    ) -> bool:
        return await self.repository.inactivate_customer(
            customer_document
        )

    async def list_all_customers(
        self, skip: int = 0, limit: int = 100
    ) -> List[Customer]:
        return await self.repository.list_all_customers(
            skip, limit
        )

    async def update_customer(
        self,
        customer_document: str,
        customer: ClientUpdate,
    ) -> Optional[Customer]:
        return await self.repository.update(
            customer_document, customer
        )
