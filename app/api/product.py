# This file contains all the endpoints related with products
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.api.authentication import verify_user
from app.models.authentication import UserResponse
from app.models.product import (
    CreateProduct,
    Product, 
    ProductUpdate
)
from app.services.product import ProductService
from app.utils.products import validate_empty_str, validate_product_data

# Instace the main router
router = APIRouter()

# Instance the router
router = APIRouter(
    prefix="/product",
    tags=["Products"],
    responses={
        404: {
            "description": "Not found, please contact the admin"
        }
    },
)

# Instace the main service class for products
# Singleton pattern
service = ProductService()

@router.post(
    "/create-product",
    response_model = Product,
    status_code = status.HTTP_201_CREATED,
)
async def create_product(
    product: CreateProduct,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Creates a new product.

    This endpoint allows the creation of a new product in the system.
    It requires the user to be authenticated and authorized.
    - The numeric values within the product data must be positive.
    - The profit margin is calculated based on the purchase and sale prices.

    **Args**: 
    - product (CreateProduct): The data of the product to create.

    **Return:** The newly created product represented with the response model.

    **Raises:** a `400 Bad Request` is returned.
    """
    try:
        # Validate that the product data does not contain negative values
        validate_product_data(product)
        return await service.create_product(
            product
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/by-id/{id_product}",
    response_model=Product,
)
async def get_product_by_id(
    id_product: int,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Retrieves a product by id.

    This endpoint allows fetching a product's information using its ID number.     
    User authentication and authorization are required.

    **Args**:
    - id_product (int): The ID of the product to retrieve.

    **Returns:**
    - Product: The product data, if found.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if no product is found with the given ID.
    """
    try:
        product = await service.get_product_by_id(
            id_product
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id '{id_product}' not found",
            )
        return product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/products", 
    response_model=List[Product]
)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(verify_user),
):
    """
    Lists all products with pagination.

    This endpoint retrieves a list of products from the system.
    Supports pagination through `skip` and `limit` parameters.
    User authentication and authorization are required.

    **Args**:
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Maximum number of records to return. Defaults 100.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - List[Product]: A list of product objects.
    """
    try:
        return await service.list_all_products(
            skip, limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/update-product",
    response_model=Product,
)
async def update_product(
    id_product: int,
    product: ProductUpdate,
    current_user=Depends(verify_user),
):
    """
    Updates a products's information.

    This endpoint allows updating an existing product's
    data using its ID number. The user must be
    authenticated and authorized.

    **Args**:
    - id_product (int): The id of the product to update.
    - product (ProductUpdate): The updated data for the product.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - Customer: The updated product data.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if the customer with the given document is not found.
    """
    try:
        # Validate that the product data does not contain negative values
        validate_product_data(product)
        # Validate that the product name and description are not empty strings
        validate_empty_str(
            product.product_name,
            field_name="Product name"
        )
        validate_empty_str(
            product.product_description,
            field_name="Product description"
        )
        # update the product
        updated_product = (
            await service.update_product(
                id_product, product
            )
        )
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Current product '{id_product}' not found",
            )
        return updated_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.delete(
    "/delete-product/{id_producto}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    id_producto: int,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Deletes a product by ID.

    This endpoint allows the deletion of a product from the system
    using its ID number. It requires the user to be authenticated
    and authorized.

    **Args**:
    - id_producto (int): The ID of the product to delete.

    **Returns:**
    - None

    **Raises:**
    - HTTPException:
    - `404 Not Found` if the product could not be found or deleted.
    """
    try:
        if not await service.delete_product(
            id_producto
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id '{id_producto}' not found or could not be deleted",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

