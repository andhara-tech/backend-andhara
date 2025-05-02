from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.authentication import verify_user
from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
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
    """
    Retrieves all purchases for a customer by document number.

    This endpoint fetches the complete purchase history for a customer,
    including detailed product information for each purchase and the
    total historical purchase amount. It requires the user to be
    authenticated and authorized.

    **Args**:
    - document (str): The customer's document number used to filter purchases.
                     Must be a valid document number (5-20 characters).

    **Returns**:
    - PurchaseByCustomerDocumentResponse:
        A structured response containing:
        - historical_purchases (float): The customer's lifetime total spent
        - purchases (list[PurchaseResponse]): Detailed list of all purchases
          Each purchase includes:
            - Purchase metadata (dates, IDs)
            - List of purchased products with details
            - Calculated totals

    **Raises**:
    - HTTPException:
        - `404 Not Found` if no customer exists with the given document.
        - `422 Unprocessable Entity` if the document format is invalid.
        - `500 Internal Server Error` for unexpected database errors.

    **Notes**:
    - Purchases are returned in descending date order (most recent first).
    - Each product includes VAT calculations for accurate financial reporting.
    - Requires valid JWT authentication via the verify_user dependency.
    """
    try:
        return await service.get_purchases_by_customer_document(document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.patch(
    "/toggle-customer/{document}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_user)],
)
async def toggle_customer(document: str, activate: bool) -> Customer:
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
        response = await service.toggle_customer(document, activate)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error inactivating the customer",
            )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/customers", dependencies=[Depends(verify_user)])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    search: Annotated[
        str | None, Query(description="Filter by phone number")
    ] = None,
) -> list[Customer]:
    """
    Lists all customers with pagination and optional search filtering.

    This endpoint retrieves a paginated list of customers, allowing filtering
    by a search term across multiple fields (e.g., customer_document,
    first name, last name, email, phone_number, and home_address). Supports
    pagination through `skip` and `limit` query parameters. User
    authentication and authorization are required.

    **Args:**
    - search (str, optional): Search term to filter customers. Matches
      partially across customer_document, customer_first_name,
      customer_last_name, email, phone_number, and home_address.
      Defaults to None.
    - skip (int, optional): Number of records to skip for pagination.
      Defaults to 0.
    - limit (int, optional): Maximum number of records to return per page.
      Defaults to 100.
    - current_user: The authenticated user, injected via dependency.

    **Returns:**
    - List[CustomerResponse]: A paginated list of customer objects. If a search
      term is provided, the list is filtered to include only matching records.

    **Raises:**
    - HTTPException 404: If no customers are found matching the search term
      or pagination criteria.
    """
    try:
        return await service.list_all_customers(skip, limit, search)
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
) -> Customer:
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
