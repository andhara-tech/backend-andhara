"""Module for purchase services."""

from app.models.purchase import PurchaseResponse, SaleCreate
from app.persistence.repositories.purchase import PurchaseRepository


class PurchaseService:
    def __init__(self) -> None:
        self.repository: PurchaseRepository = PurchaseRepository()

    async def make_purchase(self, purchase: SaleCreate) -> PurchaseResponse:
        return await self.repository.make_purchase(purchase)
