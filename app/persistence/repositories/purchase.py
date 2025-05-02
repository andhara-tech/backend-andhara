from datetime import date, timedelta

from fastapi import HTTPException, status
from supabase import Client  # noqa: TC002

from app.models.purchase import (
    DeliveryResponse,
    PaymentResponse,
    ProductInPurchaseResponse,
    PurchaseResponse,
    SaleCreate,
)
from app.persistence.db.connection import get_supabase


class PurchaseRepository:
    """Class for the purchase repository."""  # noqa: D203

    def __init__(self) -> None:
        self.supabase: Client = get_supabase()

    async def make_purchase(self, purchase: SaleCreate) -> PurchaseResponse:  # noqa: C901, PLR0912, PLR0915
        # 1. Validate the customer data
        customer_response = (
            self.supabase.table("customer")
            .select("customer_document, customer_state")
            .eq("customer_document", purchase.customer_document)
            .execute()
        )
        if not customer_response.data:
            msg = f"Customer data is invalid for customer with document {
                purchase.customer_document
            }"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            )

        if not customer_response.data[0].get("customer_state"):
            msg = f"Customer inactive. Document {purchase.customer_document}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=msg
            )

        # 2. Validate if the branch is valid and exists
        branch_response = (
            self.supabase.table("branch")
            .select("id_branch")
            .eq("id_branch", str(purchase.id_branch))
            .execute()
        )
        if not branch_response.data:
            msg = f"Branch with id {purchase.id_branch} does not exist"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            )

        # 3. Validate stock and product data in bulk
        product_ids = [str(p.id_product) for p in purchase.products]

        # Obtener stock de todos los productos en una sola consulta
        stock_response = (
            self.supabase.table("branch_stock")
            .select("id_product, quantity")
            .eq("id_branch", str(purchase.id_branch))
            .in_("id_product", product_ids)
            .execute()
        )
        stock_dict = {
            s["id_product"]: s["quantity"] for s in stock_response.data
        }

        for product in purchase.products:
            available_stock = stock_dict.get(str(product.id_product), 0)
            if available_stock < product.unit_quantity:
                msg_error = f"Product with id {
                    product.id_product
                } does not have enough stock"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
                )

        # Obtener información de todos los productos en una sola consulta
        products_response = (
            self.supabase.table("product")
            .select("id_product, sale_price, vat, product_state")
            .in_("id_product", product_ids)
            .execute()
        )
        products_dict = {p["id_product"]: p for p in products_response.data}

        products_data = []
        for product in purchase.products:
            product_info = products_dict.get(str(product.id_product))
            if not product_info:
                msg_product = f"Product not found {product.id_product}"
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=msg_product
                )

            if not product_info.get("product_state"):
                msg_product = f"Product is inactive {product.id_product}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_product
                )

            sale_price = product_info.get("sale_price")
            vat = product_info.get("vat")
            if vat <= 0:
                msg_error = f"Invalid VAT for product {
                    product.id_product
                }, VAT must be greater than 0"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
                )

            subtotal_without_vat = sale_price * product.unit_quantity
            total_price_with_vat = subtotal_without_vat * (1 + (vat / 100))
            products_data.append(
                {
                    "id_product": str(product.id_product),
                    "unit_quantity": product.unit_quantity,
                    "subtotal_without_vat": subtotal_without_vat,
                    "total_price_with_vat": total_price_with_vat,
                }
            )

        # 4. Create the purchase record in the database
        purchase_date = date.today()  # noqa: DTZ011
        next_purchase_date = purchase_date + timedelta(
            days=purchase.purchase_duration
        )
        purchase_data = {
            "customer_document": purchase.customer_document,
            "purchase_date": purchase_date.isoformat(),
            "purchase_duration": purchase.purchase_duration,
            # Calcular e insertar directamente
            "next_purchase_date": next_purchase_date.isoformat(),
        }
        purchase_response = (
            self.supabase.table("purchase").insert(purchase_data).execute()
        )
        if not purchase_response.data:
            msg_error_purchase = "Error creating purchase, please try again"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg_error_purchase,
            )

        id_purchase = purchase_response.data[0].get("id_purchase")

        # 5. Associate the purchase with the products and update stock
        for product in products_data:
            purchase_product_data = {
                "id_purchase": id_purchase,
                "id_product": product.get("id_product"),
                "unit_quantity": product.get("unit_quantity"),
                "subtotal_without_vat": product.get("subtotal_without_vat"),
                "total_price_with_vat": product.get("total_price_with_vat"),
            }
            purchase_product_response = (
                self.supabase.table("purchase_product")
                .insert(purchase_product_data)
                .execute()
            )

            if not purchase_product_response.data:
                self.supabase.table("purchase").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                msg_error = "Error creating purchase product, please try again"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
                )

            current_stock = (
                self.supabase.table("branch_stock")
                .select("quantity")
                .eq("id_branch", str(purchase.id_branch))
                .eq("id_product", str(product.get("id_product")))
                .execute()
            )
            new_stock = current_stock.data[0].get("quantity") - product.get(
                "unit_quantity"
            )
            stock_update_response = (
                self.supabase.table("branch_stock")
                .update({"quantity": new_stock})
                .eq("id_branch", str(purchase.id_branch))
                .eq("id_product", str(product.get("id_product")))
                .execute()
            )
            if not stock_update_response.data:
                self.supabase.table("purchase").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                self.supabase.table("purchase_product").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                msg_error = "Error updating stock, please try again"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
                )

        # 6. Record the payment
        if purchase.remaining_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Remaining balance cannot be negative",
            )

        payment_data = {
            "id_purchase": id_purchase,
            "payment_type": purchase.payment_type,
            "payment_status": purchase.payment_status,
            "remaining_balance": purchase.remaining_balance,
        }
        payment_response = (
            self.supabase.table("payment").insert(payment_data).execute()
        )
        if not payment_response.data:
            for product in products_data:
                current_stock = (
                    self.supabase.table("branch_stock")
                    .select("quantity")
                    .eq("id_branch", str(purchase.id_branch))
                    .eq("id_product", str(product.get("id_product")))
                    .execute()
                )
                reverted_stock = current_stock.data[0].get(
                    "quantity"
                ) + product.get("unit_quantity")
                self.supabase.table("branch_stock").update(
                    {"quantity": reverted_stock}
                ).eq("id_branch", str(purchase.id_branch)).eq(
                    "id_product", str(product.get("id_product"))
                ).execute()
            self.supabase.table("purchase_product").delete().eq(
                "id_purchase", id_purchase
            ).execute()
            self.supabase.table("purchase").delete().eq(
                "id_purchase", id_purchase
            ).execute()
            msg_error = "Error creating payment, please try again"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
            )

        payment = payment_response.data[0]

        # 7. Record the delivery (if applicable)
        delivery = None
        if purchase.delivery_type:
            delivery_data = {
                "id_purchase": id_purchase,
                "delivery_type": purchase.delivery_type,
                "delivery_status": "Sin Preparar",
                "delivery_cost": purchase.delivery_cost,
                "delivery_comment": purchase.delivery_comment,
            }
            delivery_response = (
                self.supabase.table("delivery").insert(delivery_data).execute()
            )
            if not delivery_response.data:
                self.supabase.table("payment").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                for product in products_data:
                    current_stock = (
                        self.supabase.table("branch_stock")
                        .select("quantity")
                        .eq("id_branch", str(purchase.id_branch))
                        .eq("id_product", str(product.get("id_product")))
                        .execute()
                    )
                    reverted_stock = current_stock.data[0].get(
                        "quantity"
                    ) + product.get("unit_quantity")
                    self.supabase.table("branch_stock").update(
                        {"quantity": reverted_stock}
                    ).eq("id_branch", str(purchase.id_branch)).eq(
                        "id_product", str(product.get("id_product"))
                    ).execute()
                self.supabase.table("purchase_product").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                self.supabase.table("purchase").delete().eq(
                    "id_purchase", id_purchase
                ).execute()
                msg_error = "Error creating delivery, please try again"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=msg_error
                )
            delivery = delivery_response.data[0]

        # 8. Build and return the response
        return PurchaseResponse(
            id_purchase=id_purchase,
            customer_document=purchase.customer_document,
            purchase_date=purchase_date,
            purchase_duration=purchase.purchase_duration,
            next_purchase_date=next_purchase_date,
            products=[
                ProductInPurchaseResponse(
                    id_product=product["id_product"],
                    unit_quantity=product["unit_quantity"],
                    subtotal_without_vat=product["subtotal_without_vat"],
                    total_price_with_vat=product["total_price_with_vat"],
                )
                for product in products_data
            ],
            payment=PaymentResponse(
                id_payment=payment["id_payment"],
                id_purchase=payment["id_purchase"],
                payment_type=payment["payment_type"],
                payment_status=payment["payment_status"],
                remaining_balance=payment["remaining_balance"],
            ),
            delivery=DeliveryResponse(
                id_delivery=delivery["id_delivery"],
                id_purchase=delivery["id_purchase"],
                delivery_type=delivery["delivery_type"],
                delivery_status=delivery["delivery_status"],
                delivery_cost=delivery["delivery_cost"],
                delivery_comment=delivery["delivery_comment"],
            )
            if delivery
            else None,
        )
