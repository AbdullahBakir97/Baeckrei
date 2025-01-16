from decimal import Decimal
from typing import Protocol, Dict, Any, Optional, Callable
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product
from .exceptions import (
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError
)
import logging

logger = logging.getLogger(__name__)

class CartOperation(Protocol):
    """Protocol defining cart operations interface."""
    def execute(self, cart: Cart, product: Optional[Product] = None, quantity: Optional[int] = None) -> None:
        """Execute cart operation."""
        pass

class AddItemOperation:
    """Strategy for adding items to cart."""
    def execute(self, cart: Cart, product: Product, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError(quantity=quantity)
        
        # Check if adding this quantity would exceed available stock
        existing_item = cart.items.filter(product=product).first()
        total_quantity = quantity
        if existing_item:
            total_quantity += existing_item.quantity
            
        if product.stock < total_quantity:
            raise InsufficientStockError(
                item=product.name,
                required_quantity=total_quantity,
                available_stock=product.stock
            )
        
        with transaction.atomic():
            cart_item = cart.add_item(product, quantity)
            product.stock -= quantity
            product.save()
            logger.info(f"Added/Updated {quantity} x {product.name} to cart {cart.id}")

class UpdateQuantityOperation:
    """Strategy for updating item quantities."""
    def execute(self, cart: Cart, product: Product, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError(quantity=quantity)
        
        current_item = cart.items.filter(product=product).first()
        if not current_item:
            raise CartNotFoundError(f"Product {product.id} not found in cart")
        
        quantity_diff = quantity - current_item.quantity
        
        with transaction.atomic():
            if quantity_diff > 0:
                # Check if we have enough stock for the increase
                if product.stock < quantity_diff:
                    raise InsufficientStockError(
                        item=product.name,
                        required_quantity=quantity_diff,
                        available_stock=product.stock
                    )
                product.stock -= quantity_diff
            else:
                # Return stock for decreased quantity
                product.stock += abs(quantity_diff)
            
            product.save()
            cart_item = cart.update_item(product, quantity)
            logger.info(f"Updated quantity to {quantity} for {product.name} in cart {cart.id}")

class RemoveItemOperation:
    """Strategy for removing items from cart."""
    def execute(self, cart: Cart, product: Product, quantity: None = None) -> None:
        cart_item = cart.items.filter(product=product).first()
        if cart_item:
            with transaction.atomic():
                # Return the stock
                product.stock += cart_item.quantity
                product.save()
                cart.remove_item(product)
                logger.info(f"Removed {cart_item.quantity} x {product.name} from cart {cart.id}")

class ClearCartOperation:
    """Strategy for clearing the cart."""
    def execute(self, cart: Cart, product: None = None, quantity: None = None) -> None:
        with transaction.atomic():
            # Return stock for all items
            for item in cart.items.all():
                item.product.stock += item.quantity
                item.product.save()
                logger.info(f"Returning {item.quantity} stock for {item.product.name}")
            cart.clear()
            logger.info(f"Cleared cart {cart.id}")

class CartService:
    """Service class to manage cart operations using strategy pattern."""

    def __init__(self, cart_id: int):
        """Initialize the cart service with operations mapping."""
        try:
            self.cart = Cart.objects.get(id=cart_id)
            if self.cart.completed:
                raise CartAlreadyCheckedOutError(f"Cart {cart_id} is no longer active.")
            
            # Initialize operations mapping with direct operation instances
            # No lambdas needed here as operations handle their own logic
            self._operations: Dict[str, CartOperation] = {
                'add': AddItemOperation(),  # Complex business logic, needs full operation
                'remove': RemoveItemOperation(),  # Handles stock return logic
                'update': UpdateQuantityOperation(),  # Complex quantity validation
                'clear': ClearCartOperation()  # Handles multiple item removal
            }
            logger.info(f"CartService initialized for cart {cart_id}")
        except Cart.DoesNotExist:
            raise CartNotFoundError(cart_id=cart_id)

    def execute_operation(self, operation: str, product_id: Optional[int] = None, 
                        quantity: Optional[int] = None) -> Dict[str, Any]:
        """Execute a cart operation using the strategy pattern."""
        try:
            operation_handler = self._operations.get(operation)
            if not operation_handler:
                logger.error(f"Invalid cart operation attempted: {operation}")
                raise ValueError(f"Invalid operation: {operation}")

            logger.info(f"Executing cart operation: {operation} for cart {self.cart.id}")
            
            # Get product if needed
            product = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    logger.info(f"Found product: {product.name} (ID: {product.id})")
                except Product.DoesNotExist:
                    logger.error(f"Product not found: {product_id}")
                    raise ValueError(f"Product with ID {product_id} not found")

            # Execute operation and return formatted data
            operation_handler.execute(self.cart, product, quantity)
            return self._format_cart_data(True)

        except Exception as e:
            logger.exception(f"Error during cart operation {operation}: {str(e)}")
            raise

    def _format_cart_data(self, include_details: bool = True) -> Dict[str, Any]:
        """Format cart data for frontend consumption with configurable detail level."""
        items = self.cart.items.all()
        logger.info(f"Formatting cart data for cart {self.cart.id} with {items.count()} items")
        
        # Basic cart data always included
        response_data = {
            'id': self.cart.id,
            'total': str(self.cart.total),
            'total_items': self.cart.total_items,
        }
        
        # Add detailed information if requested
        if include_details:
            formatted_items = []
            for item in items:
                formatted_item = {
                    'id': item.id,
                    'product': {
                        'id': item.product.id,
                        'name': item.product.name,
                        'price': str(item.product.price),
                        'stock': item.product.stock
                    },
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'total_price': str(item.total_price)
                }
                
                # Add image only if it exists
                if item.product.image:
                    formatted_item['product']['image'] = item.product.image.url
                
                formatted_items.append(formatted_item)
                logger.debug(f"Formatted cart item: {formatted_item}")
            
            # Add detailed fields
            response_data.update({
                'items': formatted_items,
                'subtotal': str(self.cart.subtotal),
                'tax': str(self.cart.tax)
            })
        
        logger.info(f"Cart data formatted: {response_data}")
        return response_data

    def add_item(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Add a product to the cart."""
        return self.execute_operation('add', product_id, quantity)

    def remove_item(self, product_id: int) -> Dict[str, Any]:
        """Remove an item from the cart."""
        return self.execute_operation('remove', product_id)

    def update_quantity(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Update the quantity of a specific item."""
        return self.execute_operation('update', product_id, quantity)

    def clear_cart(self) -> Dict[str, Any]:
        """Clear all items from the cart."""
        return self.execute_operation('clear')

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price of the cart."""
        return self.cart.total

    @property
    def item_count(self) -> int:
        """Get the total quantity of items in the cart."""
        return self.cart.total_items

    def get_cart_data(self, include_details: bool = True) -> Dict[str, Any]:
        """Get formatted cart data."""
        return self._format_cart_data(include_details)