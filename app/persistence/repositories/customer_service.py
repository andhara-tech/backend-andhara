
# This file manage the interaction with the database for customer service operations.
from typing import Any, List, Optional

from pydantic import UUID4

from app.models.customer_service import (
    CreateCustomerServiceDB,
    CustomerServiceDB,
    CustomerServiceCustomerInfo,
    CustomerServicePurchase,
    ManageCustomerServicePayload,
    ProductInPurchaseResponse
)
from app.persistence.db.connection import get_supabase

class CustomerServiceRepository:
    def __init__(self) -> None:
        self.supabase = get_supabase()
        self.table = "customer_service"

    async def create_customer_service(
        self,
        customer_service_payload: CreateCustomerServiceDB
    ) -> Optional[CustomerServiceDB]:
        """
        Create a new customer service record.
        - Returns the created CustomerServiceDB object.
        """
        try:
            print("customer_service_payload",customer_service_payload)
            response = (
                self.supabase.table(self.table)
                .insert(customer_service_payload.model_dump(mode="json"))
                .execute()
            )
            if response.data:
                return CustomerServiceDB(**response.data[0])
            return None
        except Exception as e:
            print(f"Error en Supabase al crear el servicio de cliente: {e}")
            return None

    async def list_all_cust_services(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Optional[List[CustomerServiceDB]]:
        """
        Retrieve all customer services that have an active status.
        - Returns a list of CustomerServiceDB objects.
        """
        select_query = (
            "id_customer_service, service_date, next_contact_date, id_purchase, "
            "contact_comment, customer_service_status, "
            "purchase:id_purchase ( "
            "   customer_document,"
            "   customer:customer_document ( "
            "       customer_first_name, customer_last_name, phone_number, id_branch, "
            "       branch:id_branch ( branch_name )"
            "   )"
            ")"
        )
        
        try:
            response = (
                self.supabase.table(self.table)
                .select(select_query)
                .eq("customer_service_status", True)
                .order("service_date", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )
            if response.data:
                services = [CustomerServiceDB(**item) for item in response.data]
                return services
            return []
        except Exception as e:
            print(f"Error en Supabase al obtener servicios de cliente: {e}")
            return []

    async def manage_customer_service(
        self,
        id_customer_service: UUID4,
        customer_service_payload: ManageCustomerServicePayload
    ) -> bool:
        update_data = {
            "customer_service_status": customer_service_payload.customer_service_status,
            "contact_comment": customer_service_payload.contact_comment
        }
        try:
            response = (
                self.supabase.table(self.table)
                .update(update_data)
                .eq("id_customer_service", str(id_customer_service)) # Convert UUID4 business logic to string for Supabase compatibility
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error en Supabase al actualizar customer service {id_customer_service}: {e}")
            return False

    async def get_customer_service_by_id_for_validation(
        self,
        id_customer_service: UUID4,
    ) -> Optional[CustomerServiceDB]:
        """
        Retrieves a customer service record by its ID for validation purposes -> Manage customer service endpoint.
        """
        
        select_query = (
            "id_customer_service, contact_comment, customer_service_status, id_purchase, "
            "next_contact_date, service_date, "
             "purchase:id_purchase ( "
            "   customer_document,"
            "   customer:customer_document ( "
            "       customer_first_name, customer_last_name, phone_number, id_branch, "
            "       branch:id_branch ( branch_name )"
            "   )"
            ")"
        )
        try: 
            response = (
                self.supabase.table(self.table)
                .select(select_query)
                .eq("id_customer_service", str(id_customer_service))
                .maybe_single()
                .execute()
            )
            if response.data:
                return CustomerServiceDB(**response.data)
            return None
        except Exception as e:
            print(f"Error en Supabase al validar id_customer_service {id_customer_service}: {e}")
            return None
    
    async def get_customer_info_for_service_detail(
        self,
        id_customer_service: UUID4 
    ) -> Optional[CustomerServiceCustomerInfo]:
        """
        Fetches customer information related to a customer_service record. -> used in the detail endpoint.
        """
        try:
            query = (
                "purchase:id_purchase ( "
                "   customer_document, "
                "   customer:customer_document ( "
                "       customer_first_name, customer_last_name, phone_number, email, home_address, "
                "       branch:id_branch ( branch_name )"
                "   )"
                ")"
            )
            response = (
                self.supabase.table(self.table)
                .select(query)
                .eq("id_customer_service", str(id_customer_service))
                .maybe_single()
                .execute()
            )
            if response.data and response.data.get("purchase") and response.data["purchase"].get("customer"):
                customer_data = response.data["purchase"]["customer"]
                branch_data = customer_data.get("branch", {})

                customer_info_dict = {
                    "customer_document": response.data["purchase"]["customer_document"],
                    "customer_first_name": customer_data["customer_first_name"],
                    "customer_last_name": customer_data["customer_last_name"],
                    "phone_number": customer_data.get("phone_number"),
                    "email": customer_data.get("email"),
                    "home_address": customer_data.get("home_address"),
                    "branch_name": branch_data.get("branch_name", "N/A") # Default value if branch_name is not present
                }
                return CustomerServiceCustomerInfo(**customer_info_dict)
            return None
        except Exception as e:
            print(f"Error en Supabase al obtener el cliente del servicio {id_customer_service}: {e}")
            return None
        
    async def get_purchase_info_for_service_detail(
        self, id_customer_service: UUID4
    ) -> Optional[CustomerServicePurchase]:
        """
        Fetches purchase information related to a customer_service record.
        This is shaped for the CustomerServiceDetailResponse.
        """
        try:
            query = (
                "id_purchase, next_contact_date, "
                "purchase:id_purchase ( "
                "   purchase_date, "
                "   payment ( payment_status, payment_type ), "
                "   purchase_product ( "
                "       id_product, unit_quantity, subtotal_without_vat, total_price_with_vat "
                "   ) "
                ")"
            )

            response = (
                self.supabase.table(self.table)
                .select(query)
                .eq("id_customer_service", str(id_customer_service)) # Convert UUID4 business logic to string for Supabase compatibility
                .maybe_single() # Returns a single object or None if it doesn't exist
                .execute()
            )
            
            if response.data and response.data.get("purchase"):
                purchase_data = response.data["purchase"]
                # Ensure that 'payment' exists and contains elements before accessing it
                payment_info_list = purchase_data.get("payment", [])
                payment_info = payment_info_list[0] if payment_info_list else {}

                products_list = []
                raw_products = purchase_data.get("purchase_product", [])
                for product_item in raw_products:
                    products_list.append(ProductInPurchaseResponse(**product_item))

                # Create the dictonary with the expected structure
                purchase_info_dict = {
                    "id_purchase": response.data["id_purchase"],
                    "next_contact_date": response.data["next_contact_date"],
                    "purchase_date": purchase_data["purchase_date"],
                    "payment_type": payment_info.get("payment_type", "N/A"),
                    "payment_status": payment_info.get("payment_status", "N/A"),
                    "products": products_list
                }
                return CustomerServicePurchase(**purchase_info_dict)
            return None
        except Exception as e:
            print(f"Error en Supabase al obtener la compra del servicio {id_customer_service}: {e}")
            return None   
