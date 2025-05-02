from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    CustomerByDocumentResponse,
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

    async def get_customer_by_document(
        self, document: str
    ) -> CustomerByDocumentResponse:
        customer = await self.repository.get_customer_by_document(document)
        if not customer:
            msg = f"Customer with document '{document}' not found"
            raise Exception(msg)
        return customer

    async def toggle_customer(self, document: str, status: bool) -> bool:
        return await self.repository.toggle_customer(document, status)

    async def list_all_customers(  # noqa: PLR0913
        self,
        skip: int,
        limit: int,
        first_name: str | None = None,
        last_name: str | None = None,
        document: str | None = None,
        phone_number: str | None = None,
    ) -> list[Customer]:
        return await self.repository.list_all_customers(
            skip, limit, first_name, last_name, document, phone_number
        )

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
