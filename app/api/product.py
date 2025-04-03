# This file contains all the endpoints related with products
from fastapi import APIRouter, Depends

from app.api.authentication import (
    get_current_user,
)
from app.models.authentication import BaseUser

router = APIRouter(
    prefix="/product",
    tags=["product"],
    responses={
        404: {
            "description": "Not found, please contact the admin"
        }
    },
)


@router.get("/product")
def test_product(
    user: BaseUser = Depends(get_current_user),
):
    return {"message": "Exito"}
