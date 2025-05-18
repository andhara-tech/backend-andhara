
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path

from app.api.authentication import verify_user

from app.models.customer_service import (
    CustomerServiceDetailResponse,
    CustomerServiceForTable,
    ManageCustomerServicePayload
)
from app.services.customer_service import CustomerServiceService

router = APIRouter(
    prefix="/customer-service",
    tags=["Customer Service"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Recurso no encontrado"},
    },
)

# Función para inyectar el servicio
def get_customer_service() -> CustomerServiceService:
    return CustomerServiceService()

@router.get(
    "/list-all",
    response_model=Optional[List[CustomerServiceForTable]],
    summary="Listar todos los seguimientos de compras activos",
    dependencies=[Depends(verify_user)]
)
async def list_customer_services_endpoint(
    skip: int = 0,
    limit: int = 100,
    service: CustomerServiceService = Depends(get_customer_service)
) -> Optional[List[CustomerServiceForTable]]:
    """
    Retrieve all customer services for table view.
    - `skip` and `limit` are used for pagination.
    """
    try:
        services = await service.list_all_customer_services_for_table(skip=skip, limit=limit)
        if services is None: 
            return []
        return services
    except Exception as e:
        print("Error list all:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al listar los servicios al cliente.",
        )


@router.get(
    "/get-by-id/{id_customer_service}",
    response_model=CustomerServiceDetailResponse,
    summary="Obtener el detalle de un seguimiento activo buscando por ID",
    dependencies=[Depends(verify_user)]
)
async def get_customer_service_by_id_endpoint(
    id_customer_service: UUID = Path(..., description="El UUID del servicio al cliente"),
    service: CustomerServiceService = Depends(get_customer_service)
) -> CustomerServiceDetailResponse:
    """
    Get the details of a customer service by its ID.
    - `id_customer_service` is the UUID of the customer service.
    - Return a detailed response model [Customer information - Purchase information - Last purchases]
    """
    try:
        customer_service_detail = await service.get_customer_service_detail_by_id(id_customer_service)
        if not customer_service_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio al cliente con ID {id_customer_service} no encontrado."
            )
        return customer_service_detail
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        print("Error get by ID:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al obtener el servicio al cliente.",
        )


@router.patch(
    "/manage/{id_customer_service}",
    response_model=str,
    summary="Gestionar (actualizar) un seguimiento de compra",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_user)]
)
async def manage_customer_service_endpoint(
    payload: ManageCustomerServicePayload,
    id_customer_service: UUID = Path(..., description="El UUID del servicio al cliente a gestionar"),
    service: CustomerServiceService = Depends(get_customer_service)
) -> str:
    """
    Update a customer service with the provided payload.
    - Comment is mandatory and should not be empty.
    - Status is not mandatory, by default it will be set to True (Active).
    """
    try:    
        response = await service.manage_customer_service(
            id_customer_service=id_customer_service,
            payload=payload
        )

        if response:
            return f"customer_service {id_customer_service} updated"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el servicio al cliente. Verifique los datos o el estado del servicio."
            )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        print("Error manage:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al gestionar el servicio al cliente.",
        )
