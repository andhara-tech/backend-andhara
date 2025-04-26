from __future__ import annotations

from supabase import Client  # noqa: TC002

from app.models.customer import (
    ClientUpdate,
    CreateClient,
    Customer,
    CustomerBasic,
)
from app.persistence.db.connection import get_supabase


class CustomerRepository:
    def __init__(self) -> None:
        self.supabase: Client = get_supabase()

    async def create_customer(self, customer: CreateClient) -> Customer:
        response = (
            self.supabase.table("customer").insert(customer.dict()).execute()
        )
        if not response.data:
            msg = "Error creating customer"
            raise ValueError(msg)
        return await self.get_customer_by_document(
            response.data[0]["customer_document"],
        )

    async def get_customer_by_document(
        self,
        document: str,
        all_purchases: bool = False,
    ) -> Customer | None:
        # Consulta principal para cliente y sede
        query = (
            self.supabase.table("customer")
            .select(
                """
                customer_document, document_type, customer_first_name,
                customer_last_name, phone_number, email, home_address,
                customer_state, id_branch,
                branch:branch(id_branch, branch_name, manager_name,
                    branch_address, city:city(id_city, city_name,
                        department:department(id_department, department_name)))
                """,
            )
            .eq("customer_document", document)
        )
        customer_response = query.execute()

        if not customer_response.data:
            return None

        customer_data = customer_response.data[0]

        # Consulta para el último pedido
        purchase_query = (
            self.supabase.table("purchase")
            .select(
                """
                id_purchase, purchase_date, purchase_duration,
                next_purchase_date, purchase_product:purchase_product(
                    id_product, unit_quantity, subtotal_without_vat,
                    total_price_with_vat, product:product(product_name))
                """,
            )
            .eq("customer_document", document)
            .order("purchase_date", desc=True)
        )
        if not all_purchases:
            purchase_query = purchase_query.limit(1)

        purchase_response = purchase_query.execute()

        # Procesar los datos
        branch_data = customer_data.get("branch", {})
        city_data = branch_data.get("city", {}) if branch_data else {}
        department_data = city_data.get("department", {}) if city_data else {}
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
                    }
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
            }
            if branch_data
            else None,
            "last_purchase": {
                "id_purchase": last_purchase["id_purchase"],
                "purchase_date": last_purchase["purchase_date"],
                "purchase_duration": last_purchase["purchase_duration"],
                "next_purchase_date": last_purchase.get("next_purchase_date"),
                "total_purchase": total_purchase,
                "products": products,
            }
            if last_purchase
            else None,
        }

        return Customer(**response_data)

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

    async def list_all_customers(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        # Consulta principal para clientes y sedes
        query = (
            self.supabase.table("customer")
            .select(
                """
                customer_document, document_type, customer_first_name,
                customer_last_name, phone_number, email, home_address,
                customer_state, id_branch, branch:branch(id_branch,branch_name,
                manager_name, branch_address,city:city(id_city, city_name,
                department:department(id_department, department_name)))
                """,
            )
            .range(skip, skip + limit - 1)
        )
        customers_response = query.execute()

        customers = []
        for customer_data in customers_response.data:
            # Consulta para el último pedido
            purchase_query = (
                self.supabase.table("purchase")
                .select(
                    """
                    id_purchase, purchase_date, purchase_duration,
                    next_purchase_date, purchase_product:purchase_product(
                    id_product, unit_quantity, subtotal_without_vat,
                    total_price_with_vat, product:product(product_name))
                    """,
                )
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
                }
                if branch_data
                else None,
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

        return await self.get_by_document(document=customer_document)

    async def get_customers_basic_data(self) -> list[CustomerBasic]:
        response = (
            self.supabase.table("customer")
            .select(
                """
                    customer_document, customer_first_name, customer_last_name
                """
            )
            .execute()
        )
        return response.data
