from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.api.authentication import verify_user
from app.models.authentication import UserResponse
from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
)
from app.services.client import CustomerService

# Instace the main router
router = APIRouter()

# Instance the router
router = APIRouter(
    prefix="/customer",
    tags=["Customers"],
    responses={
        404: {
            "description": "Not found, please contact the admin"
        }
    },
)

# Instace the main service class for customers
# Singleton pattern
service = CustomerService()


@router.post(
    "/create-customer",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    customer: CreateClient,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Creates a new customer.

    This endpoint allows the creation of a new customer in the system.
    It requires the user to be authenticated and authorized.

    **Args**: customer, The data required to create the customer.

    **Return:** The newly created customer represented with the response model.

    **Raises:** a `400 Bad Request` is returned.
    """
    try:
        return await service.create_customer(
            customer
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/by-document/{document}",
    response_model=Customer,
)
async def get_customer_by_document(
    document: str,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Retrieves a customer by document.

    This endpoint allows fetching a customer's information
    using their document number. It requires the user to be
    authenticated and authorized.

    **Args**:
    - document (str): The document number of the customer to retrieve.

    **Returns:**
    - Customer: The customer data, if found.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if no customer is found with the given document.
    """
    try:
        customer = await service.get_customer_by_document(
            document
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with document '{document}' not found",
            )
        return customer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/delete-customer/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    document: str,
    current_user: UserResponse = Depends(
        verify_user
    ),
):
    """
    Deletes a customer by document.

    This endpoint allows the deletion of a customer from the system
    using their document number. It requires the user to be authenticated
    and authorized.

    **Args**:
    - document (str): The document number of the customer to delete.

    **Returns:**
    - None

    **Raises:**
    - HTTPException:
    - `404 Not Found` if the customer could not be found or deleted.
    """
    try:
        if not await service.delete_customer(
            document
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error deleting the current customer",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/customers", response_model=List[Customer]
)
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(verify_user),
):
    """
    Lists all customers with pagination.

    This endpoint retrieves a list of customers from the system.
    Supports pagination through `skip` and `limit` parameters.
    User authentication and authorization are required.

    **Args**:
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Maximum number of records to return. Defaults 100.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - List[Customer]: A list of customer objects.
    """
    try:
        return await service.list_all_customers(
            skip, limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/update-customer/{customer_document}",
    response_model=Customer,
)
async def update_customer(
    customer_document: str,
    customer: ClientUpdate,
    current_user=Depends(verify_user),
):
    """
    Updates a customer's information.

    This endpoint allows updating an existing customer's
    data using their document number. The user must be
    authenticated and authorized.

    **Args**:
    - customer_document (str): The document number of the customer to update.
    - customer (ClientUpdate): The updated data for the customer.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - Customer: The updated customer data.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if the customer with the given document is not found.
    """
    try:
        updated_client = (
            await service.update_customer(
                customer_document, customer
            )
        )
        if not updated_client:
            raise HTTPException(
                status_code=404,
                detail=f"Current customer '{customer_document}' not found",
            )
        return updated_client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
