import pytest
from decimal import Decimal
from django.utils import timezone
from apps.cart.models import Cart, CartItem
from apps.products.models import Product


@pytest.mark.django_db
class TestCartQuerySet:
    def test_active_carts(self, test_cart, test_completed_cart):
        """Test filtering active carts."""
        active_carts = Cart.objects.active()
        assert test_cart in active_carts
        assert test_completed_cart not in active_carts
    
    def test_completed_carts(self, test_cart, test_completed_cart):
        """Test filtering completed carts."""
        completed_carts = Cart.objects.completed()
        assert test_completed_cart in completed_carts
        assert test_cart not in completed_carts
    
    def test_expired_carts(self, test_cart):
        """Test filtering expired carts."""
        # Set cart modified_at time to 25 hours ago using update to bypass auto_now
        Cart.objects.filter(id=test_cart.id).update(
            modified_at=timezone.now() - timezone.timedelta(hours=25)
        )
        test_cart.refresh_from_db()
        
        expired_carts = Cart.objects.expired()
        assert test_cart in expired_carts
    
    def test_for_customer(self, test_customer, test_customer_cart, test_cart):
        """Test filtering carts by customer."""
        customer_carts = Cart.objects.for_customer(test_customer)
        assert test_customer_cart in customer_carts
        assert test_cart not in customer_carts
    
    def test_for_session(self, test_guest_cart, test_cart):
        """Test filtering carts by session."""
        session_carts = Cart.objects.for_session('test_session_key')
        assert test_guest_cart in session_carts
        assert test_cart not in session_carts
    
    def test_with_total_value(self, test_cart_with_item):
        """Test annotating carts with total value."""
        cart = Cart.objects.with_total_value().get(pk=test_cart_with_item.pk)
        expected_total = test_cart_with_item.items.first().quantity * test_cart_with_item.items.first().unit_price
        assert cart.total_value == expected_total

    def test_get_for_update_with_version(self, test_cart):
        """Test getting cart with version validation."""
        from apps.cart.exceptions import VersionConflict
        from django.db import transaction

        # Get current version
        current_version = test_cart.version

        with transaction.atomic():
            # Should succeed with correct version
            cart = Cart.objects.get_for_update_with_version(test_cart.id, current_version)
            assert cart.id == test_cart.id

            # Should fail with incorrect version
            with pytest.raises(VersionConflict):
                Cart.objects.get_for_update_with_version(test_cart.id, current_version - 1)

    def test_increment_version(self, test_cart):
        """Test incrementing cart version."""
        from django.db import transaction

        # Get fresh cart from database to ensure correct version
        cart = Cart.objects.get(id=test_cart.id)
        initial_version = cart.version

        with transaction.atomic():
            # Increment version
            new_version = Cart.objects.increment_version(test_cart.id)
            assert new_version == initial_version + 1

            # Verify in database
            updated_cart = Cart.objects.get(id=test_cart.id)
            assert updated_cart.version == initial_version + 1


@pytest.mark.django_db
class TestCartItemQuerySet:
    def test_active_items(self, test_cart_with_item, test_completed_cart):
        """Test filtering active cart items."""
        active_items = CartItem.objects.active()
        assert test_cart_with_item.items.first() in active_items
        assert test_completed_cart.items.count() == 0
    
    def test_for_product(self, test_cart_with_item, test_product):
        """Test filtering items by product."""
        product_items = CartItem.objects.for_product(test_product)
        assert test_cart_with_item.items.first() in product_items
    
    def test_with_subtotal(self, test_cart_with_item):
        """Test annotating items with subtotal."""
        item = CartItem.objects.with_subtotal().get(pk=test_cart_with_item.items.first().pk)
        expected_subtotal = item.quantity * item.unit_price
        assert item.subtotal == expected_subtotal
    
    def test_out_of_stock(self, test_cart, test_product):
        """Test filtering out of stock items."""
        # Create item with quantity exceeding stock
        item = CartItem.objects.create(
            cart=test_cart,
            product=test_product,
            quantity=test_product.stock + 1,
            unit_price=test_product.price
        )
        
        out_of_stock_items = CartItem.objects.out_of_stock()
        assert item in out_of_stock_items
    
    def test_needs_price_update(self, test_cart_with_item, test_product):
        """Test filtering items needing price update."""
        # Update product price
        test_product.price = Decimal('25.99')
        test_product.save()
        
        items_needing_update = CartItem.objects.needs_price_update()
        assert test_cart_with_item.items.first() in items_needing_update

    def test_get_for_update_with_version(self, test_cart_with_item):
        """Test getting cart item with version validation."""
        from apps.cart.exceptions import VersionConflict
        from django.db import transaction

        item = test_cart_with_item.items.first()
        current_version = item.version

        with transaction.atomic():
            # Should succeed with correct version
            cart_item = CartItem.objects.get_for_update_with_version(item.id, current_version)
            assert cart_item.id == item.id

            # Should fail with incorrect version
            with pytest.raises(VersionConflict):
                CartItem.objects.get_for_update_with_version(item.id, current_version - 1)

    def test_increment_version(self, test_cart_with_item):
        """Test incrementing cart item version."""
        from django.db import transaction

        # Get fresh item from database to ensure correct version
        item = CartItem.objects.get(id=test_cart_with_item.items.first().id)
        initial_version = item.version

        with transaction.atomic():
            # Increment version
            new_version = CartItem.objects.increment_version(item.id)
            assert new_version == initial_version + 1

            # Verify in database
            updated_item = CartItem.objects.get(id=item.id)
            assert updated_item.version == initial_version + 1

    def test_get_with_stock_check(self, test_cart_with_item):
        """Test getting cart item with product for stock checking."""
        item = test_cart_with_item.items.first()
        
        # Get item with product
        item_with_product = CartItem.objects.get_with_stock_check(item.id)
        assert item_with_product.id == item.id
        assert item_with_product.product is not None
        assert item_with_product.product.id == item.product.id
