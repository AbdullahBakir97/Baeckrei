from django.db import models
from django.db.models import Q, Sum, F, DecimalField
from django.utils import timezone
from decimal import Decimal
from .exceptions import VersionConflict


class CartQuerySet(models.QuerySet):
    def active(self):
        """Get all active (not completed) carts."""
        return self.filter(completed=False)
    
    def completed(self):
        """Get all completed carts."""
        return self.filter(completed=True)
    
    def expired(self, expiry_hours=24):
        """Get all expired carts (not modified for expiry_hours and not completed)."""
        expiry_time = timezone.now() - timezone.timedelta(hours=expiry_hours)
        return self.filter(
            modified_at__lt=expiry_time,
            completed=False
        )
    
    def for_customer(self, customer):
        """Get all carts for a specific customer."""
        return self.filter(customer=customer)
    
    def for_session(self, session_key):
        """Get all carts for a specific session."""
        return self.filter(session_key=session_key)
    
    def with_total_value(self):
        """Annotate queryset with total value of all items."""
        return self.annotate(
            total_value=Sum(
                F('items__quantity') * F('items__unit_price'),
                output_field=DecimalField()
            ) or Decimal('0.00')
        )

    def get_for_update_with_version(self, cart_id, expected_version):
        """
        Get cart with lock, validating version.
        
        Args:
            cart_id: ID of cart to lock and retrieve
            expected_version: Expected version number
            
        Returns:
            Cart instance if version matches
            
        Raises:
            Cart.DoesNotExist: If cart not found
            VersionConflict: If version mismatch
        """
        cart = self.select_for_update().get(id=cart_id)
        if cart.version != expected_version:
            raise VersionConflict("Cart version mismatch")
        return cart

    def increment_version(self, cart_id):
        """
        Increment version of cart atomically.
        
        Args:
            cart_id: ID of cart to update
            
        Returns:
            New version number
        """
        from django.db.models import F
        self.filter(id=cart_id).update(version=F('version') + 1)
        return self.get(id=cart_id).version


class CartItemQuerySet(models.QuerySet):
    def active(self):
        """Get all items in active carts."""
        return self.filter(cart__completed=False)
    
    def for_product(self, product):
        """Get all cart items for a specific product."""
        return self.filter(product=product)
    
    def with_subtotal(self):
        """Annotate queryset with subtotal for each item."""
        return self.annotate(
            subtotal=F('quantity') * F('unit_price')
        )
    
    def out_of_stock(self):
        """Get items where quantity exceeds current product stock."""
        return self.filter(quantity__gt=F('product__stock'))
    
    def needs_price_update(self):
        """Get items where unit price differs from current product price."""
        return self.exclude(unit_price=F('product__price'))

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
        item = self.select_for_update().get(id=item_id)
        if item.version != expected_version:
            raise VersionConflict("Cart item version mismatch")
        return item

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
