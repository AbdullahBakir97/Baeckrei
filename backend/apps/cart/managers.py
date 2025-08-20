from django.db import models, transaction
from django.utils import timezone
from .querysets import CartQuerySet, CartItemQuerySet
from django.db import IntegrityError
from .exceptions import VersionConflict
import logging
from apps.core.services.version_service import VersionService
from apps.core.version_control.adapters import create_version_adapter

logger = logging.getLogger(__name__)

class CartManager(models.Manager):
    def get_queryset(self):
        """Return the custom CartQuerySet."""
        return CartQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get all active (not completed) carts."""
        return self.get_queryset().active()
    
    def completed(self):
        """Get all completed carts."""
        return self.get_queryset().completed()
    
    def expired(self, expiry_hours=24):
        """Get all expired carts."""
        return self.get_queryset().expired(expiry_hours)
    
    def for_customer(self, customer):
        """Get all carts for a specific customer."""
        return self.get_queryset().for_customer(customer)
    
    def for_session(self, session_key):
        """Get all carts for a specific session."""
        return self.get_queryset().for_session(session_key)
    
    def with_total_value(self):
        """Get carts annotated with total value in euros."""
        return self.get_queryset().with_total_value()
    
    def get_or_create_active_cart(self, customer=None, session_key=None):
        """
        Get or create an active cart for a customer or session.
        
        Args:
            customer: Optional customer instance
            session_key: Optional session key string
            
        Returns:
            Tuple of (cart, created)
        """
        if not customer and not session_key:
            raise ValueError("Either customer or session_key must be provided")
            
        # Try to get existing active cart
        cart_filter = {'completed': False}
        if customer:
            cart_filter['customer'] = customer
        else:
            cart_filter['session_key'] = session_key
            
        cart = self.filter(**cart_filter).first()
        
        if cart:
            return cart, False
            
        # Create new cart with initial version
        cart = self.create(
            customer=customer,
            session_key=session_key,
            version=1
        )
        return cart, True

    def get_for_update_with_version(self, cart_id, expected_version):
        """Get cart with lock and version check."""
        adapter = create_version_adapter(self.model)
        return adapter.get_with_version(cart_id, expected_version)

    def increment_version(self, cart_id):
        """Increment cart version."""
        cart = self.get(pk=cart_id)
        VersionService(self.model).optimistic_update(cart, ['version'])
        return cart.version


class CartItemManager(models.Manager):
    def get_queryset(self):
        """Return the custom CartItemQuerySet."""
        return CartItemQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get all items in active carts."""
        return self.get_queryset().active()
    
    def for_product(self, product):
        """Get all cart items for a specific product."""
        return self.get_queryset().for_product(product)
    
    def with_subtotal(self):
        """Get items annotated with subtotal."""
        return self.get_queryset().with_subtotal()
    
    def out_of_stock(self):
        """Get items where quantity exceeds current product stock."""
        return self.get_queryset().out_of_stock()
    
    def needs_price_update(self):
        """Get items where unit price differs from current product price."""
        return self.get_queryset().needs_price_update()
    
    def bulk_update_prices(self):
        """Update all cart item prices to match current product prices."""
        from django.db.models import F
        from django.db import transaction
        from .models import CartEvent
        from django.utils import timezone
        from decimal import Decimal, ROUND_HALF_UP
        
        updated_count = 0
        
        # First get all cart items that need updating
        cart_items = self.select_related('product', 'cart').filter(
            cart__completed=False,  # Only update items in active carts
            product__isnull=False   # Skip items with deleted products
        )
        
        # Process each item in its own transaction
        for item in cart_items:
            try:
                with transaction.atomic():
                    # Get fresh item and product with lock
                    item = self.select_for_update().get(pk=item.pk)
                    product = item.product.__class__.objects.get(pk=item.product.pk)
                    
                    # Convert prices to Decimal for accurate comparison
                    current_price = Decimal(str(item.unit_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    new_price = Decimal(str(product.price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    # Check if price needs updating
                    if current_price != new_price:
                        # Store old price for logging
                        old_price = current_price
                        
                        # Update item price and version
                        item.unit_price = new_price
                        item.version += 1
                        item.save(update_fields=['unit_price', 'version'])
                        updated_count += 1
                        
                        # Log price update event
                        CartEvent.objects.create(
                            cart=item.cart,
                            event_type=CartEvent.BATCH_UPDATE,
                            product=item.product,
                            quantity=item.quantity,
                            details={
                                'old_price': str(old_price),
                                'new_price': str(new_price),
                                'operation': 'price_update',
                                'item_id': str(item.pk)
                            }
                        )
                        
                        # Update cart timestamps
                        item.cart.updated_at = timezone.now()
                        item.cart.save(update_fields=['updated_at'])
                        item.cart.recalculate()
                        
            except Exception as e:
                logger.error(f"Error updating cart item {item.pk}: {str(e)}")
                continue
        
        return updated_count

    def get_for_update_with_version(self, item_id, expected_version):
        """
        Get cart item with lock, validating version.
        
        Args:
            item_id: ID of cart item to lock and retrieve
            expected_version: Expected version number
            
        Returns:
            CartItem instance if version matches
            
        Raises:
            CartItem.DoesNotExist: If item not found
            VersionConflict: If version mismatch
        """
        try:
            item = self.select_for_update().get(id=item_id)
            if item.version != expected_version:
                raise VersionConflict("Version mismatch")
            return item
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist("Cart item not found")

    def increment_version(self, item_id):
        """
        Increment version of cart item atomically.
        
        Args:
            item_id: ID of cart item to update
            
        Returns:
            New version number
        """
        from django.db.models import F
        self.filter(id=item_id).update(version=F('version') + 1)
        return self.get(id=item_id).version

    def get_with_stock_check(self, item_id):
        """
        Get cart item with related product for stock checking.
        
        Args:
            item_id: ID of cart item to retrieve
            
        Returns:
            CartItem instance with product
        """
        return self.select_related('product').get(id=item_id)
