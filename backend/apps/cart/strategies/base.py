"""Base strategy interface for cart operations."""
from typing import Protocol, Optional, TypeVar, Generic
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.core.version_control.context_managers import VersionAwareTransaction
from apps.core.version_control.base import VersionOperation
from ..models import CartItem, CartEvent
from ..services.cart_event_service import CartEventService
from django.utils import timezone

T = TypeVar('T', bound=CartItem)

class CartOperationStrategy(Protocol[T]):
    """Protocol for cart operation strategies."""
    
    def validate(self, cart_item: T, quantity: int) -> None:
        """Validate the operation."""
        ...
        
    def execute(self, cart_item: T, quantity: int) -> Optional[T]:
        """Execute the strategy."""
        ...

class BaseCartStrategy(VersionOperation[T, Optional[T]]):
    """Base implementation of cart operation strategy."""
    
    def __init__(self, event_type: str, cart: 'Cart'):
        """Initialize strategy with event type and cart."""
        self.event_type = event_type
        self.cart = cart
        self._event_service = CartEventService()
        
    def execute(self, cart_item: T, quantity: int) -> Optional[T]:
        """Execute strategy with version control."""
        try:
            with transaction.atomic():
                # Validate
                self._pre_validate(cart_item)
                self.validate(cart_item, quantity)
                
                # Lock product and validate availability
                product = cart_item.product
                with VersionAwareTransaction(product.__class__, product.pk, product.version) as locked_product:
                    # Calculate quantity change
                    current_quantity = cart_item.quantity if cart_item.pk else 0
                    quantity_change = self._calculate_change(current_quantity, quantity)
                    
                    # Handle stock
                    self._handle_stock(locked_product, quantity_change)
                    
                    # Update cart item
                    if quantity > 0:
                        cart_item.quantity = quantity
                        cart_item.unit_price = locked_product.price
                        cart_item.save()
                        result = cart_item
                    else:
                        if cart_item.pk:
                            cart_item.delete()
                        result = None
                        
                    # Log event
                    self._event_service.log_event(
                        cart=self.cart,
                        event_type=self.event_type,
                        product=locked_product,
                        quantity=abs(quantity_change),
                        details={
                            'old_stock': locked_product.stock + quantity_change,
                            'new_stock': locked_product.stock,
                            'delta': -quantity_change
                        }
                    )
                    
                    # Update cart timestamp
                    self.cart.updated_at = timezone.now()
                    self.cart.save(update_fields=['updated_at'])
                    self.cart.recalculate()
                    
                    return result
                    
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(str(e))
            
    def _pre_validate(self, cart_item: T) -> None:
        """Pre-operation validation."""
        if cart_item.cart.completed:
            raise ValidationError("Cannot modify completed cart items")
        if cart_item.version < 1:
            raise ValidationError("Invalid version number")
            
    def validate(self, cart_item: T, quantity: int) -> None:
        """Base validation."""
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
            
        if not cart_item.product.available or cart_item.product.status != 'active':
            raise ValidationError(f"Product {cart_item.product.name} is not available for purchase")
            
    def _handle_stock(self, product: 'Product', quantity_change: int) -> None:
        """Handle product stock changes."""
        if quantity_change > 0 and quantity_change > product.stock:
            raise ValidationError(f"Not enough stock. Requested: {quantity_change}, Available: {product.stock}")
            
        product.stock -= quantity_change
        product.save(update_fields=['stock', 'version'])
        
    def _calculate_change(self, current_quantity: int, new_quantity: int) -> int:
        """Calculate quantity change."""
        return new_quantity - current_quantity