"""Cart models with euro price handling."""
from django.db import models, transaction, OperationalError, DatabaseError
from django.core.cache import cache
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, TYPE_CHECKING
import uuid
import logging
import time

from apps.core.exceptions import VersionConflictError
from apps.core.models.mixins.version_mixin import VersionMixin
from apps.core.models.mixins.timestamped_mixin import TimeStampedModel
from apps.core.services.version_service import VersionService
from apps.core.version_control.context_managers import VersionAwareTransaction
from apps.products.models import Product
from apps.cart.exceptions import VersionConflict, InsufficientStockError
from .constants import *
from .managers import CartManager, CartItemManager
from .querysets import CartQuerySet, CartItemQuerySet
from .types import CartType, CartItemType, CartEventType

logger = logging.getLogger(__name__)

class Cart(VersionMixin, TimeStampedModel):
    """Model representing a shopping cart with euro prices."""
    customer = models.ForeignKey(
        'accounts.Customer',
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    _total_items = models.IntegerField(default=0, db_column='total_items')
    _subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='subtotal',
        help_text='Subtotal in euros (€)'
    )
    _tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='tax',
        help_text='Tax amount in euros (€)'
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    version = models.IntegerField(default=1, help_text="Version number for optimistic locking")
    last_modified = models.DateTimeField(auto_now=True)

    objects = CartManager.from_queryset(CartQuerySet)()

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'completed'],
                condition=models.Q(completed=False),
                name='unique_active_customer_cart'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'completed'],
                condition=models.Q(completed=False),
                name='unique_active_session_cart'
            )
        ]
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['last_modified']),
        ]

    def __str__(self) -> str:
        """Return string representation of cart."""
        owner = self.customer.email if self.customer else self.session_key
        return f"Guest Cart {self.pk} - {owner}"

    def save(self, *args, **kwargs):
        """Save cart with version control."""
        from django.db import transaction
        from apps.core.exceptions import VersionConflictError

        if self.pk:  # Only do version control for existing carts
            with transaction.atomic():
                # Get the latest version from the database
                latest = Cart.objects.select_for_update().get(pk=self.pk)

                # Check if we're forcing a version
                if 'force_version' in kwargs:
                    self.version = kwargs.pop('force_version')
                # If we're updating specific fields, increment version
                elif 'update_fields' in kwargs and 'version' in kwargs['update_fields']:
                    self.version = latest.version + 1
                # Otherwise check version match
                elif latest.version != self.version:
                    raise VersionConflictError(obj_type="Cart", obj_id=self.pk)

                # Call parent save
                super().save(*args, **kwargs)
        else:
            # New cart, no version control needed
            super().save(*args, **kwargs)

    def is_expired(self, expiry_hours=24) -> bool:
        """
        Check if cart is expired.

        Args:
            expiry_hours (int): Number of hours after which cart is considered expired. Defaults to 24.

        Returns:
            bool: True if cart is expired, False otherwise
        """
        if self.completed:
            return True

        expiry_time = timezone.now() - timezone.timedelta(hours=expiry_hours)
        if not hasattr(self, 'updated_at'):
            return False
        return self.updated_at < expiry_time

    def mark_expired(self) -> bool:
        """Mark cart as expired and completed."""
        from .commands.cart_commands import ExpireCartCommand
        try:
            command = ExpireCartCommand(self)
            return command.execute()
        except Exception as e:
            logger.error(f"Error marking cart as expired: {str(e)}")
            return False

    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def subtotal(self):
        """Calculate subtotal for all items in cart."""
        return sum(item.total_price for item in self.items.select_related('product').all()) or Decimal('0.00')

    @property
    def tax(self):
        """Calculate tax for cart."""
        from django.conf import settings
        tax_rate = Decimal(str(getattr(settings, 'CART_TAX_RATE', '0.19')))  # Default 19% tax rate
        return (self.subtotal * tax_rate).quantize(Decimal('0.01'))

    @property
    def total(self):
        """Calculate total for cart including tax."""
        return (self.subtotal + self.tax).quantize(Decimal('0.01'))

    def recalculate(self):
        """Recalculate cart totals."""
        from django.conf import settings

        # Calculate totals
        total_items = 0
        total_amount = Decimal('0.00')

        for item in self.items.all():
            total_items += item.quantity
            total_amount += item.total_price

        # Update fields
        self._total_items = total_items
        self._subtotal = total_amount
        self._tax = (self._subtotal * Decimal(str(getattr(settings, 'CART_TAX_RATE', '0.19')))).quantize(Decimal('0.01'))

    def add_item(self, product: 'Product', quantity: int) -> 'CartItem':
        """Add item to cart using command pattern."""
        from apps.cart.commands.cart_commands import AddItemCommand
        from apps.core.exceptions import VersionConflictError
        from django.db import DatabaseError
        from .utils.version_control import CartLock
        from .exceptions import InsufficientStockError, CartAlreadyCheckedOutError
        import time
        
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                with transaction.atomic():
                    # Get cart with lock and version check
                    cart = Cart.objects.select_for_update(nowait=True).get(pk=self.pk)
                    if cart.version != self.version:
                        raise VersionConflictError(obj_type="Cart", obj_id=self.pk)
                        
                    if cart.completed:
                        raise CartAlreadyCheckedOutError("Cannot add items to completed cart")
                    
                    # Execute add item command
                    command = AddItemCommand(cart, product, quantity)
                    result = command.execute()
                    
                    # Update cart version once
                    cart.version += 1
                    cart.save(update_fields=['version'], force_version=cart.version)
                    
                    # Update our instance
                    self.version = cart.version
                    return result
                    
            except (DatabaseError, OperationalError) as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(0.1 * retry_count)  # Add small delay between retries
                    self.refresh_from_db()
                    continue
            except (InsufficientStockError, CartAlreadyCheckedOutError, VersionConflictError) as e:
                raise  # Re-raise these exceptions directly
            except Exception as e:
                logger.error(f"Error executing add item command: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(0.1 * retry_count)
                    self.refresh_from_db()
                    continue
                raise
        
        # If we got here, we've exhausted all retries
        if last_error:
            logger.error(f"Failed to add item after {max_retries} retries: {str(last_error)}")
            raise VersionConflictError(obj_type="Cart", obj_id=self.pk)
        else:
            raise VersionConflictError(obj_type="Cart", obj_id=self.pk)

    def remove_item(self, product: 'Product') -> None:
        """Remove item from cart."""
        from .commands.cart_commands import RemoveItemCommand
        try:
            command = RemoveItemCommand(self, product)
            command.execute()
        except Exception as e:
            logger.error(f"Error removing item from cart: {str(e)}")
            raise ValidationError(f"Failed to remove item from cart: {str(e)}")

    def update_item_quantity(self, product: 'Product', quantity: int) -> Optional['CartItem']:
        """Update item quantity in cart with stock validation."""
        from .commands.cart_commands import UpdateItemCommand, RemoveItemCommand
        try:
            command_class = RemoveItemCommand if quantity == 0 else UpdateItemCommand
            command = command_class(self, product, quantity) if quantity > 0 else command_class(self, product)
            return command.execute()
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            raise ValidationError(str(e))

    def clear(self) -> None:
        """Clear all items from cart."""
        from .commands.cart_commands import ClearCartCommand
        try:
            command = ClearCartCommand(self)
            command.execute()
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            raise ValidationError(f"Failed to clear cart: {str(e)}")

    def _do_pre_save_version_checks(self):
        """Custom pre-save validation."""
        if self.version < 1:
            raise ValidationError("Version cannot be less than 1")

    def _update_product_quantity(self, product: 'Product', quantity_change: int, 
                               event_type: str, current_quantity: int = 0) -> Tuple['Product', bool]:
        """Update product quantity with validation."""
        from apps.cart.services.cart_event_service import CartEventService
        import uuid

        # Map operation types to event types
        event_type_mapping = {
            'ADD': 'item_added',
            'REMOVE': 'item_removed',
            'UPDATE': 'quantity_updated'
        }

        event_type = event_type_mapping.get(event_type, 'quantity_updated')

        with transaction.atomic():
            # Lock product for update
            product = Product.objects.select_for_update().get(pk=product.pk)

            # Calculate new stock level
            new_stock = product.stock - quantity_change
            old_stock = product.stock

            # Validate stock level
            if new_stock < 0:
                raise InsufficientStockError(
                    f"Insufficient stock. Requested: {abs(quantity_change)}, Available: {product.stock}"
                )

            # Update product stock
            product.stock = new_stock
            product.save(update_fields=['stock'])

            # Log event
            CartEventService().log_event(
                cart=self,
                event_type=event_type,
                product=product,
                quantity=abs(quantity_change),
                details={
                    'operation_id': str(uuid.uuid4()),
                    'old_stock': old_stock,
                    'new_stock': new_stock,
                    'delta': -quantity_change,
                    'current_quantity': current_quantity
                }
            )

            return product, True


class CartEvent(TimeStampedModel):
    """Model for tracking cart events."""
    CREATED = CART_EVENT_CREATED
    CHECKOUT_STARTED = CART_EVENT_CHECKOUT_STARTED
    CLEARED = CART_EVENT_CLEARED
    ITEM_ADDED = CART_EVENT_ITEM_ADDED
    ITEM_REMOVED = CART_EVENT_ITEM_REMOVED
    QUANTITY_UPDATED = CART_EVENT_QUANTITY_UPDATED
    STOCK_UPDATED = CART_EVENT_STOCK_UPDATED
    EXPIRED = CART_EVENT_EXPIRED
    MERGED = CART_EVENT_MERGED
    BATCH_ADD = CART_EVENT_BATCH_ADD
    BATCH_UPDATE = CART_EVENT_BATCH_UPDATE

    EVENT_TYPES = CART_EVENT_TYPES

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    details = models.JSONField(default=dict)
    metadata = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['cart', 'timestamp']),
        ]
        ordering = ['-timestamp']

    @classmethod
    def get_manager(cls):
        """Get the event logger manager lazily to avoid circular imports."""
        from .services.event_logger import CartEventLogger
        return CartEventLogger.as_manager()

    objects = property(get_manager)


class CartItem(VersionMixin, TimeStampedModel):
    """Model representing an item in a shopping cart with euro prices."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        related_name='cart_items',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Unit price in euros (€)'
    )
    version = models.IntegerField(
        default=1,
        help_text="Version number for optimistic locking"
    )

    objects = CartItemManager.from_queryset(CartItemQuerySet)()

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['version']),
        ]

    def __str__(self):
        """Return string representation of cart item."""
        return f"{self.quantity}x {self.product.name if self.product else 'Unknown'} in Cart {self.cart.id}"

    def save(self, *args, **kwargs):
        """Save cart item with version control."""
        try:
            with transaction.atomic():
                if self.pk:
                    # Get current version from database
                    current = CartItem.objects.select_for_update().get(pk=self.pk)
                    
                    # Check if we're forcing a version
                    if 'force_version' in kwargs:
                        self.version = kwargs.pop('force_version')
                    # If we're updating specific fields, increment version
                    elif 'update_fields' in kwargs and 'version' in kwargs['update_fields']:
                        self.version = current.version + 1
                    # Otherwise check version match and increment
                    elif current.version != self.version:
                        raise VersionConflict(
                            f"Version mismatch: expected {self.version}, got {current.version}",
                            obj_type=self.__class__.__name__,
                            obj_id=self.pk
                        )
                    else:
                        # Increment version on every save
                        self.version = current.version + 1
                        if 'update_fields' in kwargs:
                            kwargs['update_fields'] = list(set(kwargs['update_fields'] + ['version']))
                
                super().save(*args, **kwargs)
                
        except CartItem.DoesNotExist:
            # New item, no version check needed
            super().save(*args, **kwargs)

    def update_quantity(self, new_quantity: int) -> None:
        """
        Update item quantity with version check and stock validation.
        
        Args:
            new_quantity: New quantity to set
            
        Raises:
            ValidationError: If validation fails
            VersionConflict: If version conflict occurs
        """
        if new_quantity < 0:
            raise ValidationError("Quantity cannot be negative")
            
        try:
            with transaction.atomic():
                # Lock cart item
                cart_item = CartItem.objects.select_for_update().get(pk=self.pk)
                
                # Check version
                if cart_item.version != self.version:
                    raise VersionConflict(
                        f"Version mismatch: expected {self.version}, got {cart_item.version}",
                        obj_type=self.__class__.__name__,
                        obj_id=self.pk
                    )
                
                # Ensure cart is not completed
                if cart_item.cart.completed:
                    raise ValidationError("Cannot modify a completed cart")
                    
                # Calculate quantity change
                quantity_diff = new_quantity - cart_item.quantity
                
                if quantity_diff != 0:  # Only update if there's an actual change
                    # Update product quantity
                    product, _ = cart_item.cart._update_product_quantity(
                        product=cart_item.product,
                        quantity_change=quantity_diff,
                        event_type='UPDATE'
                    )
                    
                    # Update cart item
                    cart_item.quantity = new_quantity
                    cart_item.unit_price = product.price  # Ensure price is current
                    cart_item.version += 1
                    cart_item.save(update_fields=['quantity', 'unit_price', 'version'], force_version=cart_item.version)
                    
                    # Update cart timestamp
                    cart_item.cart.updated_at = timezone.now()
                    cart_item.cart.save(update_fields=['updated_at'])
                    cart_item.cart.recalculate()
                    
                # Refresh our instance
                self.refresh_from_db()
                
        except CartItem.DoesNotExist:
            raise ValidationError("Cart item no longer exists")
        except ValidationError:
            raise
        except VersionConflict:
            raise
        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            raise ValidationError(f"Failed to update quantity: {str(e)}")

    def clean(self):
        """Validate cart item."""
        # Check if product exists and is available
        if self.product:
            if not self.product.available or self.product.status != 'active':
                raise ValidationError({
                    'product': f'Product {self.product.name} is not available for purchase'
                })

            # For new items, validate against product stock
            if not self.pk:  # New item
                if self.quantity > self.product.stock:
                    raise ValidationError({
                        'quantity': f'Requested quantity ({self.quantity}) exceeds available stock ({self.product.stock})'
                    })
        else:
            raise ValidationError("Product no longer exists")

    @property
    def total_price(self):
        """Calculate total price for this item in euros."""
        return self.quantity * self.unit_price

    def get_formatted_total(self):
        """Get formatted total price in euros."""
        return format_price(self.total_price)

    def get_formatted_unit_price(self):
        """Get formatted unit price in euros."""
        return format_price(self.unit_price)

    @classmethod
    def get_for_update(cls, cart_id: int, product_id: int) -> Optional['CartItem']:
        """Get cart item with lock for update."""
        try:
            return cls.objects.select_for_update().get(
                cart_id=cart_id,
                product_id=product_id
            )
        except cls.DoesNotExist:
            return None
