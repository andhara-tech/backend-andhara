"""Modulo with reusable functions for customer."""

customer_queries: dict = {
    "query_customer_branch": """
        customer_document, document_type, customer_first_name,
        customer_last_name, phone_number, email, home_address,
        customer_state, id_branch,
        branch:branch(id_branch, branch_name, manager_name,
            branch_address, city:city(id_city, city_name,
                department:department(id_department, department_name)))
        """,
    "query_purchase_product": """
        id_purchase, purchase_date, purchase_duration, next_purchase_date,
        purchase_product:purchase_product(
            id_product, unit_quantity, subtotal_without_vat,
            total_price_with_vat, product:product(product_name))
        """,
    "query_customer_basic": """
        customer_document, customer_first_name, customer_last_name
        """,
}
