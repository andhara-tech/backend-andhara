from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.authentication import verify_user
from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    CustomerByDocumentResponse,
    PurchaseByCustomerDocumentResponse,
)
from app.services.customer import CustomerService

router = APIRouter(
    prefix="/customer",
    tags=["Customers"],
    responses={404: {"description": "Not found, please contact the admin"}},
)

service = CustomerService()


@router.post(
    "/create-customer",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_user)],
)
async def create_customer(customer: CreateClient) -> Customer:
    """
    Creates a new customer.

    This endpoint allows the creation of a new customer in the system.
    It requires the user to be authenticated and authorized.

    **Args**: customer, The data required to create the customer,
    including branch ID.

    **Returns:** The newly created customer with branch and last purchase
    details.

    **Raises:** HTTPException with `400 Bad Request` if creation fails.
    """
    try:
        return await service.create_customer(customer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/purchases", dependencies=[Depends(verify_user)])
async def get_purchases_by_customer_document(
    document: str,
) -> PurchaseByCustomerDocumentResponse:
    try:
        return await service.get_purchases_by_customer_document(document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.get("/by-document/{document}", dependencies=[Depends(verify_user)])
async def get_customer_by_document(
    document: str,
) -> CustomerByDocumentResponse:
    """
    Retrieves a customer by document.

    This endpoint fetches a customer's information, including their
    branch and last purchase, using their document number. It requires
    the user to be authenticated and authorized.

    **Args**:
    - document (str): The document number of the customer to retrieve.

    **Returns:**
    - Customer: The customer data with branch and last purchase details.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if no customer is found with the given document.
    """
    try:
        return await service.get_customer_by_document(document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.patch(
    "/toggle-customer/{document}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_user)],
)
async def toggle_customer(document: str, status: bool = True) -> None:
    """
    Inactivate a customer by document.

    This endpoint inactivates a customer using their document number.
    It requires the user to be authenticated and authorized.

    **Args**:
    - document (str): The document number of the customer to inactivate.

    **Returns:**
    - None

    **Raises:**
    - HTTPException:
        - `404 Not Found` if the customer could not be found or inactivated.
    """
    try:
        response = await service.toggle_customer(document, status)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error inactivating the customer",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/customers", dependencies=[Depends(verify_user)])
async def list_clients(  # noqa: PLR0913
    skip: int = 0,
    limit: int = 100,
    first_name: Annotated[
        str | None, Query(description="Customer first name")
    ] = None,
    last_name: Annotated[
        str | None, Query(description="Filter by last name")
    ] = None,
    document: Annotated[
        str | None, Query(description="Filter by document")
    ] = None,
    phone_number: Annotated[
        str | None, Query(description="Filter by phone number")
    ] = None,
) -> list[Customer]:
    """
    Lists all customers with pagination.

    This endpoint retrieves a list of customers, including their branch
    and last purchase details. Supports pagination through `skip` and `limit`
    parameters. User authentication and authorization are required.

    **Args**:
    - skip (int, optional): Number of records to skip. Defaults to 0.
    - limit (int, optional): Maximum number of records to return.
      Defaults to 100.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - List[Customer]: A list of customer objects with branch and last purchase
      details.
    """
    try:
        return await service.list_all_customers(
            skip, limit, first_name, last_name, document, phone_number
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.patch(
    "/update-customer/{customer_document}",
    dependencies=[Depends(verify_user)],
)
async def update_customer(
    customer_document: str, customer: ClientUpdate
) -> CustomerByDocumentResponse:
    """
    Updates a customer's information.

    This endpoint updates an existing customer's data, including their
    branch assignment,
    using their document number. The user must be authenticated and authorized.

    **Args**:
    - customer_document (str): The document number of the customer to update.
    - customer (ClientUpdate): The updated data for the customer.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - Customer: Updated customer data with branch and last purchase details.

    **Raises:**
    - HTTPException:
        - `404 Not Found` if the customer with the given document is not found.
    """
    try:
        return await service.update_customer(customer_document, customer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
