"""Module layer for puchases endpoints and to manage the tables."""

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.models.purchase import PurchaseResponse, SaleCreate
from app.services.authentication import verify_user
from app.services.purchase import PurchaseService

# Create the router
purchase_router = APIRouter(
    prefix="/purchase",
    tags=["Purchases"],
    responses={404: {"description": "Not found, please contact the admin"}},
)


@purchase_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_user)],
)
async def make_purchase(
    purchase: SaleCreate,
) -> PurchaseResponse:
    try:
        service = PurchaseService()
        return await service.make_purchase(purchase)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
