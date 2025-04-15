# This file constains helper fuctions for the CRUD operations of products
from typing import Union
from fastapi import HTTPException, status

from app.models.product import CreateProduct, ProductUpdate

def validate_product_data(product: Union[CreateProduct, ProductUpdate]) -> None:
    """
    Ensure that the product data, whether for creation or update, 
    does not contain any negative values.
    """
    # Validate precio_compra
    if getattr(product, "precio_compra", None) is not None and product.precio_compra < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de compra no puede ser negativo."
        )

    # Validate precio_venta
    if getattr(product, "precio_venta", None) is not None and product.precio_venta < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio de venta no puede ser un valor negativo."
        )

    # Validate descuento_producto
    if getattr(product, "descuento_producto", None) is not None and product.descuento_producto < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor de descuento para el producto no puede ser negativo."
        )

    # Validate IVA
    if getattr(product, "iva", None) is not None and product.iva < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El IVA no puede ser negativo."
        )
        
    # Validate margen_ganancia
    if getattr(product, "margen_ganancia", None) is not None and product.margen_ganancia < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El margen de ganancia no puede ser negativo."
        )

def calculate_profit_margin(precio_compra: float, precio_venta: float) -> float:
    """
    Calculate the profit margin based on the purchase and sale prices.
    - Formula: ((precio_venta - precio_compra) / precio_compra) * 100 -> porcentaje
    - Round to 2 decimal places.
    """
    if precio_compra <= 0 or precio_venta <= 0:
        raise ValueError("Para calcular el margen de ganancia el precio de compra y de venta debe ser mayor que cero.")
    
    margen_ganancia = round(
        (((precio_venta - precio_compra) / precio_compra) * 100),
        2
    )
    return margen_ganancia

def validate_empty_str(value: str, field_name: str = "Value") -> None:
    if not value.strip():  # This handles empty strings and strings with only whitespace
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} cannot be empty."
        )