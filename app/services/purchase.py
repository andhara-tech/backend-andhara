"""Module for purchase services."""

from app.models.customer_service import CreateCustomerServiceDB
from app.models.purchase import PurchaseResponse, SaleCreate
from app.persistence.repositories.customer_service import CustomerServiceRepository
from app.persistence.repositories.purchase import PurchaseRepository


class PurchaseService:
    def __init__(self) -> None:
        self.repository: PurchaseRepository = PurchaseRepository()
        self.customer_service: CustomerServiceRepository = CustomerServiceRepository()

    async def make_purchase(self, purchase: SaleCreate) -> PurchaseResponse:
        purchase_response = await self.repository.make_purchase(purchase)
         # Create customer service record
        customer_service_data = CreateCustomerServiceDB(
            id_purchase=purchase_response.id_purchase,
            service_date=purchase_response.purchase_date,
            next_contact_date=purchase_response.next_purchase_date
        )
        await self.customer_service.create_customer_service(customer_service_data)
        
        return purchase_response
