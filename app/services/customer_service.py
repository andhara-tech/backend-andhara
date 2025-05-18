
# This file manage the customer service repository
from typing import List, Optional
from datetime import date

from pydantic import UUID4

from app.models.customer_service import (
    CustomerServiceDB,
    CustomerServiceDetailResponse,
    CustomerServiceForTable,
    ManageCustomerServicePayload,
    CustomerDetail,
    PurchaseDetailForService,
    PurchaseByCustomerDocumentResponse
)

from app.persistence.repositories.customer import CustomerRepository 
from app.persistence.repositories.customer_service import CustomerServiceRepository
from app.utils.customer_service import calculate_days_remaining

class CustomerServiceService:
    def __init__(self) -> None:
        self.repository = CustomerServiceRepository()
        self.customer_repository = CustomerRepository()

    async def list_all_customer_services_for_table(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Optional[List[CustomerServiceForTable]]:
        """
        Lists customer services and transforms them into the CustomerServiceForTable format.
        """
        services_db_data: Optional[List[CustomerServiceDB]] = await self.repository.list_all_cust_services(skip=skip, limit=limit)
        
        if not services_db_data:
            return []

        processed_services_for_table: List[CustomerServiceForTable] = []
        for service_db in services_db_data:
            customer = service_db.purchase.customer
            days_remaining = None
            # Calculate days remaining 
            if service_db.next_contact_date:
                # Ensure that next_contact_date is a date object
                next_contact_date_obj = service_db.next_contact_date
                if isinstance(next_contact_date_obj, str):
                    next_contact_date_obj = date.fromisoformat(next_contact_date_obj)
                days_remaining = calculate_days_remaining(next_contact_date_obj)
            
            is_comment = bool(service_db.contact_comment and service_db.contact_comment.strip())

            try:
                # Create the model for the response
                service_entry = CustomerServiceForTable(
                    id_customer_service=service_db.id_customer_service,
                    service_date=service_db.service_date,
                    id_purchase=service_db.id_purchase,
                    customer_full_name=f"{customer.customer_first_name} {customer.customer_last_name}",
                    phone_number=customer.phone_number,
                    id_branch=customer.id_branch,
                    branch_name=customer.branch.branch_name,
                    days_remaining=days_remaining,
                    isComment=is_comment,
                    contact_comment=service_db.contact_comment,
                    customer_service_status=service_db.customer_service_status,
                )
                processed_services_for_table.append(service_entry)
            except Exception as e: 
                print(f"Error creando CustomerServiceForTable para item {service_db.id_customer_service}: {e}")
                return None

        return processed_services_for_table

    async def get_customer_service_detail_by_id(self, id_customer_service: UUID4) -> Optional[CustomerServiceDetailResponse]:
        # 1. Get the customer information
        customer_info = await self.repository.get_customer_info_for_service_detail(id_customer_service)
        if not customer_info:
            print(f"No se encontró información del cliente para el servicio {id_customer_service}")
            return None 

        # 2. Get the purchase information associated with the customer service
        purchase_info_from_service = await self.repository.get_purchase_info_for_service_detail(id_customer_service)
        if not purchase_info_from_service:
            print(f"No se encontró información de la compra para el servicio {id_customer_service}")
            return None

        # 3. Get the purchase history for the customer associated with the purchase 
        customer_purchases_history: Optional[PurchaseByCustomerDocumentResponse] = \
            await self.customer_repository.get_purchses_by_customer_document(
                customer_document=customer_info.customer_document
            )
        if not customer_purchases_history:
            print(f"No se encontró historial de compras para el cliente {customer_info.customer_document}")
            customer_purchases_history = PurchaseByCustomerDocumentResponse(historical_purchases=0.0, purchases=[])

        # Create the response model
        customer_detail = CustomerDetail(**customer_info.model_dump())

        # Set calculated fields for the purchase detail
        days_remaining_for_purchase = calculate_days_remaining(purchase_info_from_service.next_contact_date)
        subtotal_without_vat = sum(item.subtotal_without_vat for item in purchase_info_from_service.products if item.subtotal_without_vat is not None)
        total = sum(item.total_price_with_vat for item in purchase_info_from_service.products if item.total_price_with_vat is not None)

        # Create the purchase detail model
        purchase_detail = PurchaseDetailForService(
            id_purchase=purchase_info_from_service.id_purchase,
            purchase_date=purchase_info_from_service.purchase_date,
            payment_type=purchase_info_from_service.payment_type,
            payment_status=purchase_info_from_service.payment_status,
            subtotal_without_vat=subtotal_without_vat,
            total=total,
            days_remaining=days_remaining_for_purchase
        )

        return CustomerServiceDetailResponse(
            id_customer_service=id_customer_service, # The requested ID
            customer=customer_detail,
            purchase=purchase_detail,
            last_purchases=customer_purchases_history
        )

    async def manage_customer_service(
        self,
        id_customer_service: UUID4,
        payload: ManageCustomerServicePayload
    ) -> bool:
        # Validate that the customer_service exists and is active before trying to update it
        service_to_validate = await self.repository.get_customer_service_by_id_for_validation(
            id_customer_service=id_customer_service
        )

        if not service_to_validate:
            raise ValueError(f"Servicio al cliente con ID {id_customer_service} no existe.")

        if not service_to_validate.customer_service_status:
             raise ValueError(f"No es posible gestionar el servicio {id_customer_service} porque ya se encuentra cerrado.")

        if payload.customer_service_status is False and not payload.contact_comment.strip():
            raise ValueError("El comentario de contacto es requerido cuando se cierra el servicio (estado es False).")

        # Execute the update
        return await self.repository.manage_customer_service(
            id_customer_service=id_customer_service,
            customer_service_payload=payload
        )