"""Cart service implementation with enhanced version control and error handling."""
from decimal import Decimal
from typing import Protocol, Dict, Any, Optional, Tuple, List, TYPE_CHECKING
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache
from apps.cart.models import Cart, CartItem, CartEvent
from apps.products.models import Product
from apps.cart.exceptions import (
    CartException,
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError,
    CartError,
    VersionConflict
)
from apps.core.exceptions import VersionConflictError
from ..utils.cart_utils import format_price
from apps.core.version_control.context_managers import VersionAwareTransaction
from ..services.cart_event_service import CartEventService
from ..types import CartType, CartItemType, CartEventType, ProductId, Quantity
from ..commands.merge_cart_commands import MergeCartsCommand
import logging
import uuid
import time
from circuitbreaker import circuit
from functools import wraps
logger = logging.getLogger(__name__)

def with_cart_lock(func):
    @wraps(func)
    def wrapper(self, cart, *args, **kwargs):
        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(pk=cart.pk)
            if cart.completed:
                raise CartAlreadyCheckedOutError(f"Cart {cart.id} is already completed")
            return func(self, cart, *args, **kwargs)
    return wrapper

class CartService:
    """Service class to manage cart operations with enhanced version control."""

    CACHE_TIMEOUT = 3600  # 1 hour
    MAX_RETRIES = 3

    def __init__(self):
        """Initialize cart service."""
        self._event_service = CartEventService()
        logger.info("CartService initialized")

    def _validate_version(self, cart: Cart) -> None:
        """Validate cart version using CartVersionService."""
        try:
            # self._cart_version_service.get_with_version(cart.id, self._initial_version)
            pass
        except (VersionConflictError, VersionConflict) as e:
            logger.warning(f"Version conflict for cart {cart.id}: {str(e)}")
            raise

    def _increment_version(self, cart: Cart) -> None:
        """Increment cart version using CartVersionService."""
        try:
            with transaction.atomic():
                # self._cart_version_service.optimistic_update(cart, ['version'])
                # self._initial_version = cart.version
                pass
        except Exception as e:
            logger.error(f"Error incrementing version for cart {cart.id}: {str(e)}")
            raise

    @with_cart_lock
    def add_item(self, cart: Cart, product_id: ProductId, quantity: Quantity = 1) -> Dict[str, Any]:
        """Add item to cart."""
        try:
            product = self.get_product(product_id)
            cart_item = cart.add_item(product, quantity)
            return self.format_cart_data(cart)
                
        except Exception as e:
            self._handle_cart_exception(e)

    @with_cart_lock
    def update_item(self, cart: Cart, product_id: ProductId, quantity: Quantity) -> Dict[str, Any]:
        """Update item quantity."""
        try:
            product = self.get_product(product_id)
            cart_item = cart.update_item_quantity(product, quantity)
            return self.format_cart_data(cart)
                
        except Exception as e:
            self._handle_cart_exception(e)

    @with_cart_lock
    def remove_item(self, cart: Cart, product_id: ProductId) -> Dict[str, Any]:
        """Remove item from cart."""
        try:
            product = self.get_product(product_id)
            cart.remove_item(product)
            return self.format_cart_data(cart)
                
        except Exception as e:
            self._handle_cart_exception(e)

    @with_cart_lock
    def batch_add_items(self, cart: Cart, items: List[Tuple[ProductId, Quantity]]) -> Dict[str, Any]:
        """Add multiple items to cart in a single transaction."""
        try:
            added_items = []
            for product_id, quantity in items:
                product = self.get_product(product_id)
                cart_item = cart.add_item(product, quantity)
                added_items.append({
                    'product_id': str(product_id),
                    'quantity': quantity,
                    'unit_price': str(cart_item.unit_price)
                })
            
            # Log batch event
            self._event_service.log_event(
                cart=cart,
                event_type=CartEventType.BATCH_ADD,
                details={'items': added_items}
            )
            
            return self.format_cart_data(cart)
                
        except Exception as e:
            self._handle_cart_exception(e)

    @with_cart_lock
    def batch_update_quantities(self, cart: Cart, updates: List[Tuple[ProductId, Quantity]]) -> Dict[str, Any]:
        """Update quantities for multiple items in a single transaction."""
        try:
            changes = []
            for product_id, quantity in updates:
                product = self.get_product(product_id)
                cart_item = cart.update_item_quantity(product, quantity)
                
                if cart_item:  # Item wasn't removed
                    changes.append({
                        'product_id': str(product_id),
                        'new_quantity': quantity,
                        'unit_price': str(cart_item.unit_price)
                    })
            
            # Log batch update event
            if changes:
                self._event_service.log_event(
                    cart=cart,
                    event_type=CartEventType.BATCH_UPDATE,
                    details={'changes': changes}
                )
            
            return self.format_cart_data(cart)
                
        except Exception as e:
            self._handle_cart_exception(e)

    @circuit(failure_threshold=5, recovery_timeout=60)
    def get_product(self, product_id: ProductId) -> Product:
        """Get product by ID with validation and caching."""
        try:
            product = self._get_cached_product(product_id)
            
            if not product:
                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                    self._cache_product(product)
                except Product.DoesNotExist:
                    raise CartException(f"Product {product_id} not found")
                except Exception as e:
                    logger.error(f"Circuit breaker: Error fetching product {product_id}: {str(e)}")
                    raise CartException("Service temporarily unavailable")
            
            if not product.available or product.status != 'active':
                raise CartError(f"Product {product.name} is not available for purchase")
                
            return product
            
        except Exception as e:
            self._handle_cart_exception(e)

    def _get_cached_product(self, product_id: ProductId) -> Optional[Product]:
        """Get product from cache."""
        cache_key = f"product:{product_id}"
        return cache.get(cache_key)

    def _cache_product(self, product: Product) -> None:
        """Cache product with expiry."""
        cache_key = f"product:{product.id}"
        cache.set(cache_key, product, self.CACHE_TIMEOUT)

    def _handle_cart_exception(self, e: Exception) -> None:
        """Handle cart exceptions with proper formatting."""
        if isinstance(e, CartAlreadyCheckedOutError):
            logger.warning(f"Operation on completed cart: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'cart_completed',
                'detail': {'message': 'Cart is already completed'}
            })
        elif isinstance(e, InsufficientStockError):
            logger.warning(f"Stock validation failed: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'insufficient_stock',
                'detail': {
                    'message': str(e),
                    'available_stock': e.available_stock
                }
            })
        elif isinstance(e, InvalidQuantityError):
            logger.warning(f"Invalid quantity: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'invalid_quantity',
                'detail': {'message': str(e)}
            })
        elif isinstance(e, CartNotFoundError):
            logger.warning(f"Cart error: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'cart_error',
                'detail': {'message': str(e)}
            })
        elif isinstance(e, VersionConflict):
            logger.warning(f"Version conflict: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'version_conflict',
                'detail': {'message': 'Cart was modified by another process'}
            })
        elif isinstance(e, CartError):
            logger.error(f"Cart operation error: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'operation_failed',
                'detail': {'message': str(e)}
            })
        else:
            logger.error(f"Unexpected error in cart operation: {str(e)}")
            raise CartException({
                'status': 'error',
                'code': 'internal_error',
                'detail': {'message': 'An unexpected error occurred'}
            })

    def format_cart_data(self, cart: CartType) -> Dict[str, Any]:
        """Format cart data for API response."""
        items = []
        for item in cart.items.select_related('product').all():
            items.append({
                'id': str(item.id),
                'product': {
                    'id': str(item.product.id),
                    'name': item.product.name,
                    'price': format_price(item.product.price),
                    'stock': item.product.stock
                },
                'quantity': item.quantity,
                'unit_price': format_price(item.unit_price),
                'subtotal': format_price(item.total_price)
            })

        return {
            'cart': {
                'id': str(cart.id),
                'items': items,
                'total_items': cart.total_items,
                'subtotal': format_price(cart.subtotal),
                'tax': format_price(cart.tax),
                'total': format_price(cart.total)
            }
        }

    def merge_carts(self, target_cart: Cart, source_cart: Cart) -> Cart:
        """
        Merge source cart into target cart.
        
        Args:
            target_cart: Cart to merge into
            source_cart: Cart to merge from
            
        Returns:
            Updated target cart
            
        Raises:
            ValidationError: If merge is invalid
        """
        if target_cart.pk == source_cart.pk:
            raise ValidationError("Cannot merge cart with itself")
            
        if target_cart.completed or source_cart.completed:
            raise ValidationError("Cannot merge completed carts")
            
        command = MergeCartsCommand(target_cart, source_cart)
        command.execute()
        
        return target_cart
