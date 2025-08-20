"""Cart-specific version control utilities."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from functools import wraps
from apps.cart.models import Cart
from apps.core.exceptions import VersionConflictError
import logging
from typing import Optional, Tuple, Any, Callable
from apps.core.version_control.base import validate_version, with_version_lock
from apps.core.services.version_service import VersionService
from apps.core.version_control.context_managers import VersionAwareTransaction

logger = logging.getLogger(__name__)

class CartVersionService(VersionService):
    """Cart-specific version control service."""
    
    def __init__(self):
        """Initialize with Cart model."""
        super().__init__(Cart)
    
    def get_cart_with_version(self, cart_id: int) -> Tuple['Cart', int]:
        """
        Get cart and its current version.
        
        Args:
            cart_id: ID of cart to retrieve
            
        Returns:
            Tuple of (cart, version)
            
        Raises:
            Cart.DoesNotExist: If cart not found
        """
        cart = self.get_with_version(cart_id, None)  # None means don't validate version
        return cart, cart.version

    def try_lock_cart(self, cart_id: int, expected_version: int) -> Optional['Cart']:
        """
        Attempt to lock cart with version check.

        Args:
            cart_id: ID of cart to lock
            expected_version: Expected version number

        Returns:
            Cart instance if successful, None if version mismatch

        Raises:
            Cart.DoesNotExist: If cart not found
        """
        try:
            with transaction.atomic():
                cart = self.model_class.objects.select_for_update().get(pk=cart_id)
                if cart.version != expected_version:
                    return None
                return cart
        except Exception:
            return None

class CartLock:
    """Context manager for cart locking."""
    
    def __init__(self):
        """Initialize lock."""
        self._version_service = CartVersionService()
        self.cart = None
        
    def __call__(self, cart_or_func):
        """Make the lock callable for use as a decorator or with a cart instance."""
        if callable(cart_or_func):
            @wraps(cart_or_func)
            def wrapper(instance, *args, **kwargs):
                # For instance methods, get the cart from the first argument after self
                if args and isinstance(args[0], Cart):
                    self.cart = args[0]
                elif 'cart' in kwargs:
                    self.cart = kwargs['cart']
                with self:
                    return cart_or_func(instance, *args, **kwargs)
            return wrapper
        else:
            self.cart = cart_or_func
            return self
        
    def __enter__(self):
        """Lock cart and return locked instance."""
        if not self.cart:
            raise ValueError("Cart must be set before entering context")
            
        try:
            with transaction.atomic():
                locked_cart = (
                    self.cart.__class__.objects
                    .select_for_update(nowait=True)
                    .get(pk=self.cart.pk)
                )
                # Validate version
                if locked_cart.version != self.cart.version:
                    raise VersionConflictError(obj_type="Cart", obj_id=self.cart.pk)
                return locked_cart
        except Exception as e:
            logger.error(f"Error acquiring cart lock: {str(e)}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock and increment version if no error."""
        if exc_type is None and self.cart:
            try:
                with transaction.atomic():
                    # Update version atomically
                    self.cart.__class__.objects.filter(pk=self.cart.pk).update(
                        version=F('version') + 1,
                        updated_at=timezone.now()
                    )
            except Exception as e:
                logger.error(f"Error releasing cart lock: {str(e)}")
                raise

def with_cart_lock(func):
    """Decorator for cart locking operations."""
    cart_lock = CartLock()
    return cart_lock(func)

class CartItemVersionService(VersionService):
    """CartItem-specific version control service."""
    
    def __init__(self):
        """Initialize with CartItem model."""
        from ..models import CartItem
        super().__init__(CartItem)
    
    def get_item_with_version(self, item_id: int) -> Tuple['CartItem', int]:
        """
        Get cart item and its current version.
        
        Args:
            item_id: ID of cart item to retrieve
            
        Returns:
            Tuple of (cart_item, version)
            
        Raises:
            CartItem.DoesNotExist: If item not found
        """
        item = self.get_with_version(item_id, None)  # None means don't validate version
        return item, item.version

    def try_lock_item(self, item_id: int, expected_version: int) -> Optional['CartItem']:
        """
        Attempt to lock cart item with version check.

        Args:
            item_id: ID of cart item to lock
            expected_version: Expected version number

        Returns:
            CartItem instance if successful, None if version mismatch

        Raises:
            CartItem.DoesNotExist: If item not found
        """
        try:
            return self.get_with_version(item_id, expected_version)
        except Exception:
            return None

class CartItemLock:
    """Context manager for cart item locking."""
    
    def __init__(self, item):
        self.item = item
        self.locked_item = None
        
    def __enter__(self):
        """Lock cart item and return locked instance."""
        try:
            with transaction.atomic():
                self.locked_item = (
                    self.item.__class__.objects
                    .select_for_update(nowait=True)
                    .get(pk=self.item.pk)
                )
                
                if self.locked_item.version != self.item.version:
                    raise VersionConflictError(
                        f"Version mismatch: expected {self.item.version}, got {self.locked_item.version}",
                        obj_type=self.item.__class__.__name__,
                        obj_id=self.item.pk
                    )
                    
                return self.locked_item
                
        except Exception as e:
            logger.error(f"Failed to acquire lock on cart item: {str(e)}")
            raise VersionConflictError("Failed to acquire lock on cart item")
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock and increment version if no error."""
        if not exc_type and self.locked_item:
            try:
                updated = (
                    self.item.__class__.objects
                    .filter(pk=self.locked_item.pk, version=self.locked_item.version)
                    .update(
                        version=models.F('version') + 1,
                        updated_at=timezone.now()
                    )
                )
                
                if not updated:
                    raise VersionConflictError("Failed to update cart item version")
                    
                self.locked_item.refresh_from_db()
                
            except Exception as e:
                logger.error(f"Failed to release lock on cart item: {str(e)}")
                raise

def with_cart_item_lock(item):
    """Context manager for cart item locking operations."""
    return CartItemLock(item)
