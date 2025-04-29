from __future__ import annotations

from supabase import Client  # noqa: TC002

from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    CustomerByDocumentResponse,
)
from app.persistence.db.connection import get_supabase

# Import supbase quries from utils module
from app.utils.customer import customer_queries


class CustomerRepository:
    def __init__(self) -> None:
        self.supabase: Client = get_supabase()

    async def create_customer(self, customer: CreateClient) -> Customer:
        response = (
            self.supabase.table("customer").insert(customer.dict()).execute()
        )
        if not response.data:
            msg = "Error creating customer, please try again"
            raise ValueError(msg)
        # Get the customer document from the supabase response
        customer_document = response.data[0].get("customer_document")
        return await self.get_customer_by_document(customer_document)

    async def get_customer_by_document(
        self, document: str
    ) -> CustomerByDocumentResponse | None:
        # 1. Get the customer data
        query = (
            self.supabase.table("customer")
            .select(customer_queries.get("query_customer_branch"))
            .eq("customer_document", document)
        )
        customer_response = query.execute()

        if not customer_response.data:
            return None

        # Get the customer data from the supabase response
        customer_data = customer_response.data[0]

        # Search for the last purchase
        purchase_query = (
            self.supabase.table("purchase")
            .select(customer_queries.get("query_purchase_product"))
            .eq("customer_document", document)
            .order("purchase_date", desc=True)
        )
        purchase_response = purchase_query.execute()

        # Procesar los datos
        branch_data = customer_data.get("branch", {})
        city_data = branch_data.get("city", {}) if branch_data else {}
        department_data = city_data.get("department", {}) if city_data else {}
        purchases = purchase_response.data if purchase_response.data else []

        processed_purchases = []  # List to store processed purchases
        # Variable to store total historical purchases
        total_historical_purchases = 0.0

        # Iterate over the purchases
        for purchase in purchases:
            total = 0.0
            products = []

            if purchase.get("purchase_product"):
                for pp in purchase["purchase_product"]:
                    purchase_value = pp.get("total_price_with_vat", 0.0)
                    total += purchase_value
                    total_historical_purchases += purchase_value
                    products.append(
                        {
                            "id_product": pp["id_product"],
                            "product_name": pp["product"]["product_name"],
                            "unit_quantity": pp["unit_quantity"],
                            "subtotal_without_vat": pp["subtotal_without_vat"],
                            "total_price_with_vat": pp["total_price_with_vat"],
                        }
                    )

            processed_purchases.append(
                {
                    "id_purchase": purchase["id_purchase"],
                    "purchase_date": purchase["purchase_date"],
                    "purchase_duration": purchase["purchase_duration"],
                    "next_purchase_date": purchase.get("next_purchase_date"),
                    "total_purchase": total,
                    "products": products,
                }
            )

        # Estruct the frinal response
        response_data = {
            "customer_document": customer_data["customer_document"],
            "document_type": customer_data["document_type"],
            "customer_first_name": customer_data["customer_first_name"],
            "customer_last_name": customer_data["customer_last_name"],
            "phone_number": customer_data["phone_number"],
            "email": customer_data["email"],
            "home_address": customer_data["home_address"],
            "customer_state": customer_data["customer_state"],
            "total_historical_purchases": total_historical_purchases,
            "branch": {
                "id_branch": branch_data.get("id_branch"),
                "branch_name": branch_data.get("branch_name"),
                "manager_name": branch_data.get("manager_name"),
                "branch_address": branch_data.get("branch_address"),
                "city_name": city_data.get("city_name"),
                "department_name": department_data.get("department_name"),
            },
            "purchases": processed_purchases if processed_purchases else [],
        }

        return CustomerByDocumentResponse(**response_data)

    async def toggle_customer(
        self, customer_document: str, status: bool
    ) -> bool:
        response = (
            self.supabase.table("customer")
            .update({"customer_state": status})
            .eq("customer_document", customer_document)
            .execute()
        )
        return bool(response.data)

    async def list_all_customers(  # noqa: PLR0913
        self,
        skip: int = 0,
        limit: int = 100,
        first_name: str | None = None,
        last_name: str | None = None,
        document: str | None = None,
        phone_number: str | None = None,
    ) -> list[Customer]:
        # Consulta principal para clientes y sedes
        query = self.supabase.table("customer").select(
            customer_queries.get("query_customer_branch")
        )

        # Create a match case for filter usign the query params
        if first_name:
            query = query.ilike("customer_first_name", f"%{first_name}%")
        if last_name:
            query = query.ilike("customer_last_name", f"%{last_name}%")
        if document:
            query = query.ilike("customer_document", f"%{document}%")
        if phone_number:
            query = query.ilike("phone_number", f"%{phone_number}%")

        query = query.range(skip, skip + limit - 1)
        customers_response = query.execute()

        customers = []
        for customer_data in customers_response.data:
            # Consulta para el último pedido
            purchase_query = (
                self.supabase.table("purchase")
                .select(customer_queries.get("query_purchase_product"))
                .eq(
                    "customer_document",
                    customer_data["customer_document"],
                )
                .order("purchase_date", desc=True)
                .limit(1)
            )
            purchase_response = purchase_query.execute()

            # Procesar los datos
            branch_data = customer_data.get("branch", {})
            city_data = branch_data.get("city", {}) if branch_data else {}
            department_data = (
                city_data.get("department", {}) if city_data else {}
            )
            last_purchase = (
                purchase_response.data[0] if purchase_response.data else None
            )

            # Calcular el total de la compra
            total_purchase = 0
            products = []
            if last_purchase and last_purchase.get("purchase_product"):
                for pp in last_purchase["purchase_product"]:
                    total_purchase += pp["total_price_with_vat"]
                    products.append(
                        {
                            "id_product": pp["id_product"],
                            "product_name": pp["product"]["product_name"],
                            "unit_quantity": pp["unit_quantity"],
                            "subtotal_without_vat": pp["subtotal_without_vat"],
                            "total_price_with_vat": pp["total_price_with_vat"],
                        },
                    )

            # Estructurar la respuesta
            response_data = {
                "customer_document": customer_data["customer_document"],
                "document_type": customer_data["document_type"],
                "customer_first_name": customer_data["customer_first_name"],
                "customer_last_name": customer_data["customer_last_name"],
                "phone_number": customer_data["phone_number"],
                "email": customer_data["email"],
                "home_address": customer_data["home_address"],
                "customer_state": customer_data["customer_state"],
                "branch": {
                    "id_branch": branch_data.get("id_branch"),
                    "branch_name": branch_data.get("branch_name"),
                    "manager_name": branch_data.get("manager_name"),
                    "branch_address": branch_data.get("branch_address"),
                    "city_name": city_data.get("city_name"),
                    "department_name": department_data.get("department_name"),
                },
                "last_purchase": {
                    "id_purchase": last_purchase["id_purchase"],
                    "purchase_date": last_purchase["purchase_date"],
                    "purchase_duration": last_purchase["purchase_duration"],
                    "next_purchase_date": last_purchase.get(
                        "next_purchase_date",
                    ),
                    "total_purchase": total_purchase,
                    "products": products,
                }
                if last_purchase
                else None,
            }

            customers.append(Customer(**response_data))

        return customers

    async def update_customer(
        self, customer_document: str, customer: ClientUpdate
    ) -> Customer | None:
        update_data = {
            k: v for k, v in customer.dict().items() if v is not None
        }
        if not update_data:
            return await self.get_customer_by_document(
                document=customer_document
            )
        response = (
            self.supabase.table("customer")
            .update(update_data)
            .eq("customer_document", customer_document)
            .execute()
        )
        if not response.data:
            return None

        return await self.get_customer_by_document(document=customer_document)
