from django.core.exceptions import ValidationError
import pytest
from decimal import Decimal
from django.utils import timezone
from apps.cart.models import Cart, CartItem, CartEvent

pytestmark = pytest.mark.django_db

class TestCartModel:
    def test_cart_str_representation(self, test_cart):
        """Test cart string representation."""
        if test_cart.customer:
            assert str(test_cart) == f"Cart {test_cart.id} - {test_cart.customer.email}"
        else:
            assert str(test_cart) == f"Guest Cart {test_cart.id} - {test_cart.session_key}"

    def test_guest_cart_str_representation(self, guest_cart):
        """Test guest cart string representation."""
        assert str(guest_cart) == f"Guest Cart {guest_cart.id} - {guest_cart.session_key}"

    def test_cart_total_items(self, test_cart_with_item):
        """Test cart total items calculation."""
        assert test_cart_with_item.total_items == 2

    def test_cart_subtotal(self, test_cart_with_item, test_product):
        """Test cart subtotal calculation."""
        expected = Decimal('20.00')  # 10.00 * 2
        assert test_cart_with_item.subtotal == expected

    def test_cart_tax(self, test_cart_with_item):
        """Test cart tax calculation."""
        subtotal = Decimal('20.00')  # 10.00 * 2
        expected_tax = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))  # 19% VAT
        assert test_cart_with_item.tax == expected_tax

    def test_cart_total(self, test_cart_with_item):
        """Test cart total calculation."""
        subtotal = Decimal('20.00')  # 10.00 * 2
        tax = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))  # 19% VAT
        expected_total = (subtotal + tax).quantize(Decimal('0.01'))
        assert test_cart_with_item.total == expected_total

    @pytest.mark.parametrize("quantity,should_raise", [
        (5, False),    # Valid quantity
        (0, True),     # Invalid - zero quantity
        (-1, True),    # Invalid - negative quantity
        (11, True),    # Invalid - exceeds stock
    ])
    def test_add_item_validation(self, test_cart, test_product, quantity, should_raise):
        """Test adding items with various quantities."""
        if should_raise:
            with pytest.raises(ValidationError):
                test_cart.add_item(test_product, quantity)
        else:
            item = test_cart.add_item(test_product, quantity)
            assert item.quantity == quantity
            assert item.unit_price == test_product.price

    def test_update_item_quantity(self, test_cart_with_item, test_product):
        """Test updating item quantity."""
        updated_item = test_cart_with_item.update_item_quantity(test_product, 3)
        assert updated_item.quantity == 3
        test_cart_with_item.refresh_from_db()
        assert test_cart_with_item.total_items == 3

    def test_remove_item(self, test_cart_with_item, test_product):
        """Test removing item from cart."""
        test_cart_with_item.remove_item(test_product)
        assert test_cart_with_item.items.count() == 0
        assert test_cart_with_item.total_items == 0

    def test_clear_cart(self, test_cart_with_item):
        """Test clearing all items from cart."""
        test_cart_with_item.clear()
        assert test_cart_with_item.items.count() == 0
        assert test_cart_with_item.total_items == 0
        assert test_cart_with_item.subtotal == Decimal('0.00')

    def test_cart_version_increment_on_save(self, test_cart):
        """Test that cart version increments on save."""
        initial_version = test_cart.version
        test_cart.save()
        assert test_cart.version == initial_version + 1

    def test_cart_version_no_increment_when_disabled(self, test_cart):
        """Test that cart version doesn't increment when update_version=False."""
        initial_version = test_cart.version
        test_cart.save(update_version=False)
        assert test_cart.version == initial_version

    def test_cart_concurrent_modification(self, test_cart, test_product):
        """Test optimistic locking prevents concurrent modifications."""
        from apps.cart.exceptions import VersionConflict
        from apps.cart.utils.version_control import validate_cart_version
        from django.db import transaction

        # First modification
        with transaction.atomic():
            cart1 = Cart.objects.select_for_update().get(id=test_cart.id)
            original_version = cart1.version  # Store original version
            cart1.add_item(test_product, 1)
            cart1.save()

        # Get current version from database
        db_cart = Cart.objects.get(id=test_cart.id)
        db_version = db_cart.version

        # Second modification in separate transaction
        cart2 = Cart.objects.get(id=test_cart.id)
        cart2.version = original_version  # Set to original version to simulate concurrent access

        # Should fail version check when trying to validate against current db version
        with pytest.raises(VersionConflict):
            validate_cart_version(cart2, db_version)  # This should fail since cart2 has old version

class TestCartItemModel:
    def test_cart_item_str_representation(self, test_cart_with_item):
        """Test cart item string representation."""
        item = test_cart_with_item.items.first()
        expected = f"{item.quantity}x {item.product.name} in Cart {item.cart.id}"
        assert str(item) == expected

    def test_cart_item_total_price(self, test_cart_with_item):
        """Test cart item total price calculation."""
        item = test_cart_with_item.items.first()
        expected = (item.quantity * item.unit_price).quantize(Decimal('0.01'))
        assert item.total_price == expected

    def test_cart_item_clean_validation(self, test_cart, test_product):
        """Test cart item validation during clean."""
        # Test with inactive product
        test_product.status = 'inactive'
        test_product.save()
        
        item = CartItem(
            cart=test_cart,
            product=test_product,
            quantity=1,
            unit_price=test_product.price
        )
        
        with pytest.raises(ValidationError) as exc:
            item.clean()
        assert 'not available for purchase' in str(exc.value)

    def test_cart_item_version_increment(self, test_cart_with_item):
        """Test that cart item version increments on save."""
        item = test_cart_with_item.items.first()
        initial_version = item.version
        item.save()
        assert item.version == initial_version + 1

    def test_cart_item_version_no_increment_when_disabled(self, test_cart_with_item):
        """Test that cart item version doesn't increment when update_version=False."""
        item = test_cart_with_item.items.first()
        initial_version = item.version
        item.save(update_version=False)
        assert item.version == initial_version

    def test_cart_item_concurrent_modification(self, test_cart_with_item):
        """Test optimistic locking prevents concurrent item modifications."""
        from apps.cart.exceptions import VersionConflict
        from apps.cart.utils.version_control import validate_cart_version
        from django.db import transaction

        # First modification
        with transaction.atomic():
            item1 = CartItem.objects.select_for_update().get(id=test_cart_with_item.items.first().id)
            original_version = item1.version  # Store original version
            item1.quantity = 3
            item1.save()

        # Get current version from database
        db_item = CartItem.objects.get(id=item1.id)
        db_version = db_item.version

        # Second modification
        item2 = CartItem.objects.get(id=item1.id)
        item2.version = original_version  # Set to original version to simulate concurrent access

        # Should fail version check when trying to validate against current db version
        with pytest.raises(VersionConflict):
            validate_cart_version(item2, db_version)  # This should fail since item2 has old version

class TestCartEventModel:
    def test_cart_event_creation(self, test_cart, test_product):
        """Test cart event creation and ordering."""
        event = CartEvent.objects.create(
            cart=test_cart,
            event_type='ADD',
            product=test_product,
            quantity=2
        )
        assert event.event_type == 'ADD'
        assert event.quantity == 2
        assert event.cart == test_cart
        assert event.product == test_product

    def test_cart_event_ordering(self, test_cart, test_product):
        """Test cart events are ordered by timestamp descending."""
        event1 = CartEvent.objects.create(
            cart=test_cart,
            event_type='ADD',
            product=test_product,
            quantity=2
        )
        event2 = CartEvent.objects.create(
            cart=test_cart,
            event_type='UPDATE',
            product=test_product,
            quantity=3
        )
        events = CartEvent.objects.filter(cart=test_cart)
        assert events[0] == event2  # Most recent first
        assert events[1] == event1

    @pytest.mark.parametrize("quantity,expected", [
        (5, 5),  # Valid
        (15, None)  # Exceeds stock
    ])
    def test_add_item_stock_validation(self, empty_cart, active_product, quantity, expected):
        if expected:
            item = empty_cart.add_item(active_product, quantity)
            assert item.quantity == expected
        else:
            with pytest.raises(ValidationError):
                empty_cart.add_item(active_product, quantity)