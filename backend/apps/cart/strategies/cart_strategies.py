"""Cart operation strategies."""
from typing import Optional, TypeVar
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.core.version_control.base import VersionOperation
from apps.core.version_control.context_managers import VersionAwareTransaction
from ..models import Cart, CartItem, CartEvent
from ..services.cart_event_service import CartEventService
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Cart)

class ExpireCartStrategy(VersionOperation[T, bool]):
    """Strategy for marking cart as expired."""
    
    def __init__(self, cart: T):
        self.cart = cart
        self._event_service = CartEventService()
        
    def execute(self, cart: T, *args, **kwargs) -> bool:
        """Execute cart expiration."""
        try:
            with transaction.atomic():
                # Get fresh instance with lock
                db_cart = type(cart).objects.select_for_update().get(pk=cart.pk)
                
                # If already completed, just update current instance to match
                if db_cart.completed:
                    cart.completed = True
                    cart.completed_at = db_cart.completed_at
                    return True

                # Update database instance
                db_cart.completed = True
                db_cart.completed_at = timezone.now()
                db_cart.save(update_fields=['completed', 'completed_at'])

                # Log expiration event
                self._event_service.log_event(
                    cart=db_cart,
                    event_type=CartEvent.EXPIRED,
                    details={
                        'expired_at': db_cart.completed_at.isoformat() if db_cart.completed_at else None
                    }
                )

                # Update current instance to match database
                cart.completed = True
                cart.completed_at = db_cart.completed_at
                return True

        except Exception as e:
            logger.error(f"Error marking cart {cart.id} as expired: {str(e)}")
            return False

class MergeCartStrategy(VersionOperation[T, None]):
    """Strategy for merging carts with version control."""
    
    def __init__(self, target_cart: T):
        self.target_cart = target_cart
        self._event_service = CartEventService()
        
    def execute(self, source_cart: T, *args, **kwargs) -> None:
        """Execute cart merge with proper version control."""
        try:
            with transaction.atomic():
                # Lock both carts with version check
                target_cart = type(self.target_cart).objects.select_for_update(nowait=True).get(pk=self.target_cart.pk)
                source_cart = type(source_cart).objects.select_for_update(nowait=True).get(pk=source_cart.pk)
                
                # Validate cart states
                self._validate_carts(target_cart, source_cart)
                
                # Transfer items with version control
                self._transfer_items(target_cart, source_cart)
                
                # Update target cart
                self._update_target_cart(target_cart)
                
                # Log merge event
                self._log_merge_event(target_cart, source_cart)
                
        except Exception as e:
            logger.error(f"Error merging carts: {str(e)}")
            raise ValidationError(f"Failed to merge carts: {str(e)}")
            
    def _transfer_items(self, target_cart: T, source_cart: T) -> None:
        """Transfer items between carts with stock validation."""
        for source_item in source_cart.items.select_related('product').all():
            self._transfer_item(target_cart, source_item)
                
    def _transfer_item(self, target_cart: T, source_item: CartItem) -> None:
        """Transfer a single item with version control."""
        product = source_item.product
        with VersionAwareTransaction(product.__class__, product.pk, product.version) as locked_product:
            if not self._validate_product(locked_product):
                return
                
            target_item = target_cart.items.filter(product=product).first()
            if target_item:
                self._update_existing_item(target_item, source_item, locked_product)
            else:
                self._create_new_item(target_cart, source_item, locked_product)
                # Do NOT decrement product stock during cart merge. Stock will be decremented at checkout.
            # We still save the product to bump version only if necessary elsewhere; skip here to avoid side effects.
                
    def _validate_product(self, product: 'Product') -> bool:
        """Validate product availability."""
        if not product.available or product.status != 'active':
            logger.warning(f"Skipping unavailable product {product.name} during merge")
            return False
        return True
        
    def _update_existing_item(self, target_item: CartItem, source_item: CartItem, product: 'Product') -> None:
        """Update existing cart item with version control."""
        new_quantity = target_item.quantity + source_item.quantity
        if new_quantity > product.stock:
            logger.warning(f"Insufficient stock for product {product.name} during merge")
            return
            
        target_item.quantity = new_quantity
        target_item.unit_price = product.price
        target_item.version += 1
        target_item.save(update_fields=['quantity', 'unit_price', 'version'])
        
    def _create_new_item(self, target_cart: T, source_item: CartItem, product: 'Product') -> None:
        """Create new cart item with version control."""
        if source_item.quantity > product.stock:
            logger.warning(f"Insufficient stock for product {product.name} during merge")
            return
            
        CartItem.objects.create(
            cart=target_cart,
            product=product,
            quantity=source_item.quantity,
            unit_price=product.price,
            version=1
        )
        
    def _update_target_cart(self, target_cart: T) -> None:
        """Update target cart after merge."""
        target_cart.updated_at = timezone.now()
        target_cart.recalculate()
        target_cart.version += 1
        target_cart.save(force_version=target_cart.version)
        self.target_cart.version = target_cart.version
        
    def _log_merge_event(self, target_cart: T, source_cart: T) -> None:
        """Log merge event with details."""
        self._event_service.log_event(
            cart=target_cart,
            event_type=CartEvent.MERGED,
            details={
                'merged_from': str(source_cart.id),
                'items_merged': [
                    {
                        'product_id': str(item.product.id),
                        'quantity': item.quantity,
                        'unit_price': str(item.unit_price)
                    }
                    for item in source_cart.items.all()
                ]
            }
        )
        
    def _validate_carts(self, target_cart: T, source_cart: T) -> None:
        """Validate cart states before merge."""
        if target_cart.completed:
            raise ValidationError("Cannot merge into completed cart")
        if source_cart.completed:
            raise ValidationError("Cannot merge from completed cart")
        if target_cart.pk == source_cart.pk:
            raise ValidationError("Cannot merge cart with itself")
