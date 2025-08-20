"""Cart utilities with model-specific operations."""
from decimal import Decimal
from typing import List, Optional
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from .cart_base_utils import (
    format_price,
    validate_quantity,
    calculate_item_total,
    calculate_tax,
    validate_stock_level
)
from ..exceptions import StockNotAvailableError

def validate_cart_item(product: 'Product', quantity: int, cart_item: Optional['CartItem'] = None) -> None:
    """Validate cart item can be added/updated."""
    from ..models import CartItem
    
    if product is None:
        raise ValidationError("Product cannot be None")
        
    validate_quantity(quantity)
    
    if not product.available or product.status != 'active':
        raise StockNotAvailableError(
            message=f"Product {product.name} is not available for purchase",
            available_stock=0
        )
    
    total_quantity = quantity
    if cart_item:
        total_quantity += cart_item.quantity
        
    validate_stock_level(total_quantity, product.stock)

def validate_stock_availability(product: 'Product', quantity: int) -> None:
    """Validate product stock availability."""
    if not product.available:
        raise StockNotAvailableError(
            message=f"Product {product.name} is not available for purchase",
            available_stock=0
        )
        
    validate_quantity(quantity)
    validate_stock_level(quantity, product.stock)

def merge_quantities(current: int, additional: int, max_allowed: int) -> int:
    """Merge quantities with validation."""
    total = current + additional
    validate_stock_level(total, max_allowed)
    return total

def calculate_cart_totals(items: QuerySet) -> tuple[Decimal, Decimal, Decimal]:
    """Calculate cart subtotal, tax and total."""
    subtotal = sum(calculate_item_total(item.quantity, item.unit_price) for item in items)
    tax = calculate_tax(subtotal)
    total = (subtotal + tax).quantize(Decimal('0.01'))
    return subtotal, tax, total
