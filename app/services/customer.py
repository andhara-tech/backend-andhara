from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    PurchaseByCustomerDocumentResponse,
)
from app.persistence.repositories.customer import (
    CustomerRepository,
)


class CustomerService:
    def __init__(self) -> None:
        self.repository = CustomerRepository()

    async def create_customer(self, customer: CreateClient) -> Customer:
        return await self.repository.create_customer(customer)

    async def get_purchases_by_customer_document(
        self, document: str
    ) -> list[PurchaseByCustomerDocumentResponse]:
        return await self.repository.get_purchses_by_customer_document(
            document,
        )

    async def toggle_customer(self, document: str, active: bool) -> Customer:
        return await self.repository.toggle_customer(document, active)

    async def list_all_customers(
        self,
        skip: int,
        limit: int,
        search: str | None = None,
    ) -> list[Customer]:
        return await self.repository.list_all_customers(skip, limit, search)

    async def update_customer(
        self,
        document: str,
        customer: ClientUpdate,
    ) -> Customer:
        updated_customer = await self.repository.update_customer(
            document, customer
        )
        if not updated_customer:
            msg = f"Customer with document '{document}' not found"
            raise Exception(msg)
        return updated_customer
