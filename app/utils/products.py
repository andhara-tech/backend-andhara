# This file constains helper fuctions for the CRUD operations of products
from typing import Union

from fastapi import HTTPException, status

from app.models.product import (
    CreateProduct,
    ProductUpdate,
)


def validate_product_data(
    product: Union[CreateProduct, ProductUpdate],
) -> None:
    """
    Validates the fields of a product object to ensure they meet the required conditions.

    Args:
        product (Union[CreateProduct, ProductUpdate]): The product object to validate.

    Raises:
        HTTPException: If any of the following conditions are met:
            - `purchase_price` is provided and is negative.
            - `sale_price` is provided and is negative.
            - `product_discount` is provided and is negative.
            - `vat` is provided and is negative.
            - `profit_margin` is provided and is negative.
    This function ensures that all numeric fields in the product object have non-negative values.

    """
    # Validate purchase_price
    if (
        getattr(product, "purchase_price", None) is not None
        and product.purchase_price < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de compra no puede ser negativo.",
        )

    # Validate sale_price
    if (
        getattr(product, "sale_price", None) is not None
        and product.sale_price < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de venta no puede ser un valor negativo.",
        )

    # Validate product_discount
    if (
        getattr(product, "product_discount", None) is not None
        and product.product_discount < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor de descuento para el producto no puede ser negativo.",
        )

    # Validate vat
    if getattr(product, "vat", None) is not None and product.vat < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El IVA no puede ser negativo.",
        )

    # Validate profit_margin
    if (
        getattr(product, "profit_margin", None) is not None
        and product.profit_margin < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El margen de ganancia no puede ser negativo.",
        )


def calculate_profit_margin(
    purchase_price: float,
    sale_price: float,
) -> float:
    """
    Calculates the profit margin percentage based on the purchase price and sale price.

    Args:
        purchase_price (float): The cost price of the product. Must be greater than zero.
        sale_price (float): The selling price of the product. Must be greater than zero.

    Returns:
        float: The profit margin as a percentage, rounded to two decimal places.

    Raises:
        ValueError: If either `purchase_price` or `sale_price` is None.
        ValueError: If either `purchase_price` or `sale_price` is less than or equal to zero.

    Example:
        >>> calculate_profit_margin(50, 100)
        100.0

    """
    if purchase_price is None or sale_price is None:
        msg = "Para calcular el margen de ganancia el precio de compra y precio de venta son valores obligatorios."
        raise ValueError(
            msg,
        )
    if purchase_price <= 0 or sale_price <= 0:
        msg = "Para calcular el margen de ganancia el precio de compra y de venta debe ser mayor que cero."
        raise ValueError(
            msg,
        )

    return round(
        (((sale_price - purchase_price) / purchase_price) * 100),
        2,
    )


def validate_stock_quantity(
    quantity: int,
) -> bool:
    """
    Validates the stock quantity of a product.

    Args:
        quantity (int): The quantity of the product to validate.

    Returns:
        bool: True if the quantity is valid.

    Raises:
        HTTPException: If the quantity is negative, an HTTP 400 Bad Request error is raised with a descriptive message.

    """
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No es posible crear un producto con cantidad negativa en el stock.",
        )
    return True
