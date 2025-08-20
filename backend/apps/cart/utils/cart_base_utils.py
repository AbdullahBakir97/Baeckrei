"""Base cart utilities without model dependencies."""
from decimal import Decimal
from typing import Any
from django.core.exceptions import ValidationError

def format_price(price: Decimal) -> str:
    """Format price in euros using German format."""
    # Format with German style: €1.000,00
    parts = str(price).split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else '00'
    
    # Add thousands separator
    if len(integer_part) > 3:
        integer_part = f"{integer_part[:-3]}.{integer_part[-3:]}"
    
    # Format with comma for decimal and € prefix
    return f"€{integer_part},{decimal_part:0>2}"

def validate_quantity(quantity: int) -> None:
    """Validate quantity is positive."""
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0")

def calculate_item_total(quantity: int, unit_price: Decimal) -> Decimal:
    """Calculate total price for an item."""
    return (Decimal(str(quantity)) * unit_price).quantize(Decimal('0.01'))

def calculate_tax(subtotal: Decimal, rate: Decimal = Decimal('0.19')) -> Decimal:
    """Calculate tax amount using German VAT rate (19%)."""
    tax = (subtotal * rate).quantize(Decimal('0.01'))
    return tax

def validate_stock_level(requested: int, available: int) -> None:
    """Validate requested quantity against available stock."""
    if requested > available:
        from apps.cart.exceptions import StockNotAvailableError
        raise StockNotAvailableError(
            message=f'Not enough stock. Requested: {requested}, Available: {available}',
            available_stock=available
        )
