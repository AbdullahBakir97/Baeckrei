"""Cart quantity update strategies with version control."""
from django.core.exceptions import ValidationError
from django.db import transaction, OperationalError, DatabaseError
from django.utils import timezone
from typing import Literal, TypeVar, Optional, overload, Tuple, TYPE_CHECKING
from apps.core.version_control.base import VersionOperation
from apps.core.version_control.context_managers import VersionAwareTransaction
from apps.core.exceptions import VersionConflictError, VersionLockTimeoutError
from ..exceptions import VersionConflict, InsufficientStockError
from ..services.cart_event_service import CartEventService
from ..constants import (
    CART_EVENT_ITEM_ADDED,
    CART_EVENT_QUANTITY_UPDATED,
    CART_EVENT_ITEM_REMOVED
)
import uuid
import logging
import time

if TYPE_CHECKING:
    from apps.cart.models import CartItem, Cart

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='CartItem')

class BaseQuantityStrategy(VersionOperation[T, Optional[T]]):
    """Base strategy for cart quantity update operations with version control."""
    
    def __init__(self, event_type: Literal['item_added', 'quantity_updated', 'item_removed'], cart: 'Cart'):
        self.event_type = event_type
        self.cart = cart
        self._event_service = CartEventService()
        
    @overload
    def execute(self, cart_item: T, new_quantity: int) -> Optional[T]: ...
    
    def execute(self, cart_item: T, *args, **kwargs) -> Optional[T]:
        """Execute the cart quantity update operation with version control."""
        if not args:
            raise ValidationError("new_quantity is required")
        new_quantity = args[0]
        if not isinstance(new_quantity, int):
            raise ValueError("new_quantity must be an integer")
            
        try:
            # Lock product and validate availability
            product = cart_item.product.__class__.objects.select_for_update().get(pk=cart_item.product.pk)
            
            # Add a small delay to simulate real-world conditions
            time.sleep(0.1)
            
            # Validate product status
            if self.event_type != CART_EVENT_ITEM_REMOVED and (not product.available or product.status != 'active'):
                raise ValidationError(f"Product {product.name} is not available for purchase")
            
            # Calculate quantity changes
            current_quantity = cart_item.quantity if cart_item.pk else 0
            quantity_change = self._calculate_change(current_quantity, new_quantity)
            
            # Validate stock levels
            if self.event_type != CART_EVENT_ITEM_REMOVED:
                if quantity_change > 0 and quantity_change > product.stock:
                    raise InsufficientStockError(
                        f"Not enough stock. Additional requested: {quantity_change}, Available: {product.stock}"
                    )
            
            # Update product stock
            old_stock = product.stock
            new_stock = old_stock - quantity_change
            product.stock = new_stock
            product.save(update_fields=['stock'])
            
            # Update cart item
            if new_quantity > 0:
                if cart_item.pk:
                    # Get a fresh cart item with lock
                    cart_item = type(cart_item).objects.select_for_update().get(pk=cart_item.pk)
                    cart_item.quantity = new_quantity
                    cart_item.unit_price = product.price
                    cart_item.save()
                else:
                    # New item - no version control needed yet
                    cart_item.quantity = new_quantity
                    cart_item.unit_price = product.price
                    cart_item.save()
                result = cart_item
            else:
                if cart_item.pk:
                    cart_item.delete()
                result = None
            
            # Log stock change event
            self._event_service.log_event(
                cart=self.cart,
                event_type=self.event_type,
                product=product,
                quantity=abs(quantity_change),
                details={
                    'old_stock': old_stock,
                    'new_stock': new_stock,
                    'delta': -quantity_change,
                    'operation_id': str(uuid.uuid4()),
                    'source': 'quantity_strategy',
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return result
            
        except (OperationalError, DatabaseError) as e:
            raise OperationalError(str(e))
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in quantity strategy: {str(e)}")
            raise ValidationError(str(e))
            
    def _pre_validate(self, cart_item: T) -> None:
        """Pre-operation validation."""
        if cart_item.cart.completed:
            raise ValidationError("Cannot modify completed cart items")
            
    def _calculate_change(self, current_quantity: int, new_quantity: int) -> int:
        """Calculate quantity change."""
        return new_quantity - current_quantity
            
class AddQuantityStrategy(BaseQuantityStrategy[T]):
    """Strategy for adding items to cart."""
    
    def __init__(self, cart: 'Cart'):
        super().__init__(CART_EVENT_ITEM_ADDED, cart)
        
    def validate(self, cart_item: T, quantity: int):
        """Validate add operation."""
        if quantity < 1:
            raise ValidationError("Quantity must be positive")
            
class UpdateQuantityStrategy(BaseQuantityStrategy[T]):
    """Strategy for updating cart item quantities."""
    
    def __init__(self, cart: 'Cart'):
        super().__init__(CART_EVENT_QUANTITY_UPDATED, cart)
        
    def validate(self, cart_item: T, quantity: int):
        """Validate update operation."""
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
            
class RemoveQuantityStrategy(BaseQuantityStrategy[T]):
    """Strategy for removing items from cart."""
    
    def __init__(self, cart: 'Cart'):
        super().__init__(CART_EVENT_ITEM_REMOVED, cart)
        
    def _calculate_change(self, current_quantity: int, new_quantity: int) -> int:
        """Override to handle removal."""
        return -current_quantity  # Always remove all
