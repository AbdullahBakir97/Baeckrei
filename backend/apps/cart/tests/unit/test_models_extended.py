"""Extended unit tests for cart models."""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from apps.cart.models import Cart, CartItem, CartEvent
from apps.products.models import Product
from apps.accounts.models import Customer

pytestmark = pytest.mark.django_db

class TestCartModelExtended:
    """Extended tests for Cart model."""

    def test_mark_expired(self, test_cart):
        """Test cart expiration."""
        # Arrange
        assert not test_cart.completed
        assert test_cart.completed_at is None

        # Act
        test_cart.mark_expired()

        # Assert
        assert test_cart.completed
        assert test_cart.completed_at is not None
        assert test_cart.completed_at <= timezone.now()

    def test_recalculate_without_save(self, test_cart_with_item):
        """Test recalculate without saving changes."""
        # Arrange
        initial_subtotal = test_cart_with_item._subtotal
        test_cart_with_item.items.update(quantity=5)  # Update directly in DB

        # Act
        test_cart_with_item.recalculate(save_changes=False)

        # Assert
        assert test_cart_with_item._subtotal != initial_subtotal
        test_cart_with_item.refresh_from_db()
        assert test_cart_with_item._subtotal == initial_subtotal  # DB value unchanged

    def test_unique_customer_cart_constraint(self, test_customer):
        """Test unique active cart per customer constraint."""
        # Arrange
        Cart.objects.create(customer=test_customer)

        # Act & Assert
        with pytest.raises(IntegrityError):
            Cart.objects.create(customer=test_customer)

    def test_unique_session_cart_constraint(self):
        """Test unique active cart per session constraint."""
        # Arrange
        session_key = "test_session"
        Cart.objects.create(session_key=session_key)

        # Act & Assert
        with pytest.raises(IntegrityError):
            Cart.objects.create(session_key=session_key)

    def test_tax_calculation_edge_cases(self, test_cart_with_item):
        """Test tax calculation with different rates and edge cases."""
        # Arrange
        cart = test_cart_with_item
        cart_item = cart.items.first()

        # Test zero price
        with transaction.atomic():
            cart_item.unit_price = Decimal('0.00')
            cart_item.save(skip_price_update=True)
            cart.refresh_from_db()
            cart.recalculate()
            cart.refresh_from_db()
            assert cart.subtotal == Decimal('0.00')
            assert cart.tax == Decimal('0.00')

        # Test very small price
        with transaction.atomic():
            cart_item.unit_price = Decimal('0.01')
            cart_item.save(skip_price_update=True)
            cart.refresh_from_db()
            cart.recalculate()
            cart.refresh_from_db()
            expected_tax = (Decimal('0.01') * cart_item.quantity * Decimal('0.19')).quantize(Decimal('0.01'))
            assert cart.tax == expected_tax

        # Test large price
        with transaction.atomic():
            cart_item.unit_price = Decimal('9999.99')
            cart_item.save(skip_price_update=True)
            cart.refresh_from_db()
            cart.recalculate()
            cart.refresh_from_db()
            expected_tax = (Decimal('9999.99') * cart_item.quantity * Decimal('0.19')).quantize(Decimal('0.01'))
            assert cart.tax == expected_tax

    def test_update_item_quantity_nonexistent_product(self, test_cart):
        """Test updating quantity for non-existent product."""
        # Arrange
        non_existent_product = Product(id=999)

        # Act & Assert
        with pytest.raises(ValidationError) as exc:
            test_cart.update_item_quantity(non_existent_product, 1)
        assert "not found in cart" in str(exc.value)


class TestCartItemModelExtended:
    """Extended tests for CartItem model."""

    def test_formatted_price_methods(self, test_cart_with_item):
        """Test formatted price methods."""
        # Arrange
        cart_item = test_cart_with_item.items.first()
        
        # Update price in a transaction to prevent auto-updates
        with transaction.atomic():
            # Disable version increment and price update for this test
            cart_item.unit_price = Decimal('123.45')
            cart_item.quantity = 2
            cart_item.save(update_version=False, skip_price_update=True)
            
            # Force refresh to get the new values
            cart_item.refresh_from_db()
            
            # Verify the values are set correctly
            assert cart_item.unit_price == Decimal('123.45'), f"Unit price is {cart_item.unit_price}"
            # Test German number format (comma for decimal separator)
            # Unit price should be 123.45 formatted as €123,45
            assert cart_item.get_formatted_unit_price() == '€123,45'
            # Total price should be 246.90 formatted as €246,90
            assert cart_item.get_formatted_total() == '€246,90'

    def test_get_for_update_success(self, test_cart_with_item):
        """Test get_for_update with existing item."""
        # Arrange
        cart_item = test_cart_with_item.items.first()

        # Act
        result = CartItem.get_for_update(cart_item.cart_id, cart_item.product_id)

        # Assert
        assert result is not None
        assert result.id == cart_item.id

    def test_get_for_update_nonexistent(self, test_cart, test_product):
        """Test get_for_update with non-existent item."""
        # Act
        result = CartItem.get_for_update(test_cart.id, test_product.id)

        # Assert
        assert result is None

    @pytest.mark.django_db(transaction=True)
    def test_update_quantity_with_deleted_product(self, test_cart_with_item):
        """Test updating quantity when product is deleted."""
        # Arrange
        cart_item = test_cart_with_item.items.first()
        product = cart_item.product

        # Store references before deletion
        cart_item_id = cart_item.id
        product_id = product.id

        # Delete the product in a separate transaction
        with transaction.atomic():
            # Delete the product first
            Product.objects.filter(id=product_id).delete()
            
            # Get the cart item and verify product is now NULL
            cart_item.refresh_from_db()
            assert cart_item.product is None

        # Try to update quantity and expect error
        with pytest.raises(ValidationError) as exc:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.update_quantity(5)

        assert "Product no longer exists" in str(exc.value)

    def test_update_quantity_with_insufficient_stock(self, test_cart_with_item):
        """Test updating quantity when stock becomes unavailable."""
        # Arrange
        cart_item = test_cart_with_item.items.first()
        cart_item.product.stock = 1
        cart_item.product.save()

        # Act & Assert
        with pytest.raises(ValidationError) as exc:
            cart_item.update_quantity(5)
        assert "Not enough stock" in str(exc.value)

    def test_unit_price_auto_update(self, test_cart_with_item):
        """Test unit price auto-update when product price changes."""
        # Arrange
        cart_item = test_cart_with_item.items.first()
        new_price = Decimal('99.99')
        
        # Act
        cart_item.product.price = new_price
        cart_item.product.save()
        cart_item.save()  # This should trigger the auto-update

        # Assert
        cart_item.refresh_from_db()
        assert cart_item.unit_price == new_price


class TestCartEventModelExtended:
    """Extended tests for CartEvent model."""

    def test_event_types(self, test_cart_with_item):
        """Test different event types."""
        # Arrange
        cart = test_cart_with_item
        product = cart.items.first().product

        # Test REMOVE event
        CartEvent.objects.create(cart=cart, event_type='REMOVE', product=product, quantity=1)
        assert CartEvent.objects.filter(event_type='REMOVE').exists()

        # Test UPDATE event
        CartEvent.objects.create(cart=cart, event_type='UPDATE', product=product, quantity=2)
        assert CartEvent.objects.filter(event_type='UPDATE').exists()

        # Test CLEAR event
        CartEvent.objects.create(cart=cart, event_type='CLEAR', product=None, quantity=None)
        assert CartEvent.objects.filter(event_type='CLEAR').exists()

    def test_event_product_deletion(self, test_cart_with_item):
        """Test event behavior when referenced product is deleted."""
        # Arrange
        cart = test_cart_with_item
        product = cart.items.first().product
        event = CartEvent.objects.create(cart=cart, event_type='ADD', product=product, quantity=1)

        # Act
        product.delete()
        event.refresh_from_db()

        # Assert
        assert event.product is None  # Should be set to NULL

    def test_event_ordering(self, test_cart):
        """Test event ordering by timestamp."""
        # Arrange
        now = timezone.now()
        
        # Create events with different timestamps
        event1 = CartEvent.objects.create(
            cart=test_cart,
            event_type='ADD',
            timestamp=now - timedelta(hours=2)
        )
        event2 = CartEvent.objects.create(
            cart=test_cart,
            event_type='UPDATE',
            timestamp=now - timedelta(hours=1)
        )
        event3 = CartEvent.objects.create(
            cart=test_cart,
            event_type='CLEAR',
            timestamp=now
        )

        # Act
        events = CartEvent.objects.filter(cart=test_cart)

        # Assert
        assert list(events) == [event3, event2, event1]  # Most recent first
