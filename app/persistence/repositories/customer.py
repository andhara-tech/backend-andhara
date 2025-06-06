from __future__ import annotations

from datetime import datetime

from supabase import Client  # noqa: TC002

from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    PurchaseByCustomerDocumentResponse,
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

    async def get_purchses_by_customer_document(
        self, customer_document: str
    ) -> PurchaseByCustomerDocumentResponse:
        # Validate if the customer exists
        customer_response = (
            self.supabase.table("customer")
            .select("customer_document")
            .eq("customer_document", customer_document)
            .execute()
        )
        if not customer_response.data:
            msg = "Customer not found"
            raise ValueError(msg)

        purchase_query = (
            self.supabase.table("purchase")
            .select(customer_queries.get("query_purchase_product"))
            .eq("customer_document", customer_document)
            .order("purchase_date", desc=True)
        )
        purchase_response = purchase_query.execute()
        purchases = purchase_response.data if purchase_response.data else []

        historical_purchases = 0.0
        processed_purchases = []
        for purchase in purchases:
            total = 0.0
            products = []
            if purchase.get("purchase_product"):
                for pp in purchase["purchase_product"]:
                    purchase_value = pp.get("total_price_with_vat", 0.0)
                    total += purchase_value
                    historical_purchases += purchase_value
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

        response_data = {
            "historical_purchases": historical_purchases,
            "purchases": processed_purchases,
        }
        return PurchaseByCustomerDocumentResponse(**response_data)

    async def get_customer_by_document(self, document: str) -> Customer:
        # Look for the customer data
        customer_response = (
            self.supabase.table("customer")
            .select(customer_queries.get("query_customer_branch"))
            .eq("customer_document", document)
            .execute()
        )
        # Validate if the customer exists
        if not customer_response.data:
            msg = "Customer not found"
            raise ValueError(msg)

        customer_response = customer_response.data[0]
        # Make the purchase query
        purchase_query = (
            self.supabase.table("purchase")
            .select(customer_queries.get("query_purchase_product"))
            .eq("customer_document", document)
            .order("purchase_date", desc=True)
            .limit(1)
        )
        purchase_response = purchase_query.execute()
        branch_data = customer_response.get("branch", {})
        city_data = branch_data.get("city", {}) if branch_data else {}
        department_data = city_data.get("department", {}) if city_data else {}
        last_purchase = (
            purchase_response.data[0] if purchase_response.data else None
        )
        # Get the last purchase and its total
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

        response_data = {
            "customer_document": customer_response["customer_document"],
            "document_type": customer_response["document_type"],
            "customer_first_name": customer_response["customer_first_name"],
            "customer_last_name": customer_response["customer_last_name"],
            "phone_number": customer_response["phone_number"],
            "email": customer_response["email"],
            "home_address": customer_response["home_address"],
            "customer_state": customer_response["customer_state"],
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
        return Customer(**response_data)

    async def toggle_customer(
        self, customer_document: str, active: bool
    ) -> Customer:
        toggle_response = (
            self.supabase.table("customer")
            .update({"customer_state": active})
            .eq("customer_document", customer_document)
            .execute()
        )
        if not toggle_response.data:
            msg = "Error changing the customer status"
            raise ValueError(msg)
        return await self.get_customer_by_document(customer_document)

    async def list_all_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Customer]:
        # Consulta principal para clientes y sedes
        query = self.supabase.table("customer").select(
            customer_queries.get("query_customer_branch")
        )

        # Create a match case for filter using the query params
        if search and search.strip():
            search_item = search.strip()
            # Agregar comodines para coincidencias parciales
            search_pattern = f"%{search_item}%"

            # Lista de condiciones para la consulta
            conditions = []

            # Si el término es numérico, buscar en columnas numéricas
            if search_item.isnumeric():
                conditions.extend(
                    [
                        f"customer_document.ilike.{search_pattern}",
                        f"phone_number.ilike.{search_pattern}",
                    ]
                )
            elif " " in search_item:
                search_words = search_item.split()
                for word in search_words:
                    word_pattern = f"%{word}%"
                    conditions.extend(
                        [
                            f"customer_first_name.ilike.{word_pattern}",
                            f"customer_last_name.ilike.{word_pattern}",
                        ]
                    )
            else:
                conditions.extend(
                    [
                        f"customer_document.ilike.{search_pattern}",
                        f"customer_first_name.ilike.{search_pattern}",
                        f"customer_last_name.ilike.{search_pattern}",
                        f"email.ilike.{search_pattern}",
                        f"phone_number.ilike.{search_pattern}",
                        f"home_address.ilike.{search_pattern}",
                    ]
                )

            # Unir todas las condiciones con OR
            or_clause = ",".join(conditions)
            query = query.or_(or_clause)

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

        # Sort the customers by last purchase date
        return sorted(
            customers,
            key=lambda x: (
                x.last_purchase.purchase_date
                if x.last_purchase and x.last_purchase.purchase_date
                else datetime.min.date()  # noqa: DTZ901
            ),
            reverse=True,
        )

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
