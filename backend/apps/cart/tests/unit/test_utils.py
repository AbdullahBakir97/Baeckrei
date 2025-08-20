import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.cart.utils import (
    calculate_cart_totals,
    format_price,
    generate_cart_id,
    validate_stock_availability,
    calculate_item_total,
    merge_quantities,
    validate_cart_item,
    get_cart_with_version,
    get_cart_item_with_version,
    try_lock_cart,
    try_lock_cart_item,
    validate_cart_version,
    increment_versions
)
from apps.cart.exceptions import StockNotAvailableError, VersionConflict
from apps.cart.models import Cart, CartItem

@pytest.mark.django_db
class TestCartUtils:
    def test_calculate_cart_totals(self, test_cart_with_item):
        """Test cart total calculations."""
        cart_items = test_cart_with_item.items.all()
        subtotal, tax, total = calculate_cart_totals(cart_items)
        
        # Product price is 10.00 and quantity is 2
        expected_subtotal = Decimal('20.00')  # 10.00 * 2
        expected_tax = (expected_subtotal * Decimal('0.19')).quantize(Decimal('0.01'))  # 19% German VAT
        expected_total = (expected_subtotal + expected_tax).quantize(Decimal('0.01'))
        
        assert subtotal == expected_subtotal
        assert tax == expected_tax
        assert total == expected_total

    @pytest.mark.parametrize(
        "price,expected",
        [
            (Decimal('10.00'), '€10,00'),
            (Decimal('10.10'), '€10,10'),
            (Decimal('11.00'), '€11,00'),
            (Decimal('0.00'), '€0,00'),
            (Decimal('1000.00'), '€1.000,00'),
        ]
    )
    def test_format_price(self, price, expected):
        """Test price formatting."""
        assert format_price(price) == expected

    def test_generate_cart_id(self):
        """Test cart ID generation."""
        cart_id = generate_cart_id()
        assert isinstance(cart_id, str)
        assert len(cart_id) == 32  # MD5 hash length
        
        # Test uniqueness
        another_cart_id = generate_cart_id()
        assert cart_id != another_cart_id

    def test_validate_stock_availability_success(self, test_product):
        """Test successful stock validation."""
        validate_stock_availability(test_product, 5)  # Should not raise exception

    def test_validate_stock_availability_failure(self, test_product):
        """Test stock validation failure."""
        with pytest.raises(StockNotAvailableError):
            validate_stock_availability(test_product, test_product.stock + 1)

    def test_validate_stock_availability_zero_stock(self, test_product):
        """Test validation with zero stock."""
        test_product.stock = 0
        test_product.save()
        with pytest.raises(StockNotAvailableError) as exc_info:
            validate_stock_availability(test_product, 1)
        assert exc_info.value.available_stock == 0

    def test_validate_stock_availability_inactive_product(self, test_product):
        """Test validation with inactive product."""
        test_product.available = False
        test_product.save()
        with pytest.raises(StockNotAvailableError):
            validate_stock_availability(test_product, 1)

    def test_calculate_item_total(self):
        """Test item total calculation."""
        quantity = 3
        unit_price = Decimal('10.00')
        expected_total = Decimal('30.00')
        assert calculate_item_total(quantity, unit_price) == expected_total

    def test_merge_quantities_success(self):
        """Test successful quantity merging."""
        current = 2
        additional = 3
        max_stock = 10
        assert merge_quantities(current, additional, max_stock) == 5

    def test_merge_quantities_exceeds_stock(self):
        """Test quantity merging exceeding stock."""
        current = 5
        additional = 6
        max_stock = 10
        with pytest.raises(StockNotAvailableError):
            merge_quantities(current, additional, max_stock)

    def test_validate_cart_item_success(self, test_product):
        """Test successful cart item validation."""
        validate_cart_item(test_product, 5)  # Should not raise exception

    def test_validate_cart_item_invalid_product(self):
        """Test cart item validation with invalid product."""
        with pytest.raises(ValidationError):
            validate_cart_item(None, 5)

    def test_validate_cart_item_invalid_quantity(self, test_product):
        """Test cart item validation with invalid quantity."""
        with pytest.raises(ValidationError):
            validate_cart_item(test_product, 0)

    def test_validate_cart_item_exceeds_stock(self, test_product):
        """Test cart item validation with quantity exceeding stock."""
        with pytest.raises(StockNotAvailableError):
            validate_cart_item(test_product, test_product.stock + 1)

@pytest.mark.django_db
class TestVersionControlUtils:
    def test_get_cart_with_version(self, test_cart_with_item):
        """Test getting cart with version."""
        cart, version = get_cart_with_version(test_cart_with_item.id)
        assert cart.id == test_cart_with_item.id
        assert version == test_cart_with_item.version

    def test_get_cart_item_with_version(self, test_cart_with_item):
        """Test getting cart item with version."""
        cart_item = test_cart_with_item.items.first()
        item, version = get_cart_item_with_version(cart_item.id)
        assert item.id == cart_item.id
        assert version == cart_item.version

    def test_try_lock_cart_success(self, test_cart_with_item):
        """Test successful cart locking."""
        cart = try_lock_cart(test_cart_with_item.id, test_cart_with_item.version)
        assert cart is not None
        assert cart.id == test_cart_with_item.id

    def test_try_lock_cart_version_mismatch(self, test_cart_with_item):
        """Test cart locking with version mismatch."""
        wrong_version = test_cart_with_item.version + 1
        cart = try_lock_cart(test_cart_with_item.id, wrong_version)
        assert cart is None

    def test_try_lock_cart_item_success(self, test_cart_with_item):
        """Test successful cart item locking."""
        cart_item = test_cart_with_item.items.first()
        item = try_lock_cart_item(cart_item.id, cart_item.version)
        assert item is not None
        assert item.id == cart_item.id

    def test_try_lock_cart_item_version_mismatch(self, test_cart_with_item):
        """Test cart item locking with version mismatch."""
        cart_item = test_cart_with_item.items.first()
        wrong_version = cart_item.version + 1
        item = try_lock_cart_item(cart_item.id, wrong_version)
        assert item is None

    def test_validate_cart_version_success(self, test_cart_with_item):
        """Test successful cart version validation."""
        validate_cart_version(test_cart_with_item, test_cart_with_item.version)

    def test_validate_cart_version_mismatch(self, test_cart_with_item):
        """Test cart version validation with mismatch."""
        wrong_version = test_cart_with_item.version + 1
        with pytest.raises(VersionConflict):
            validate_cart_version(test_cart_with_item, wrong_version)

    def test_increment_versions(self, test_cart_with_item):
        """Test incrementing versions of multiple objects."""
        cart_item = test_cart_with_item.items.first()
        original_cart_version = test_cart_with_item.version
        original_item_version = cart_item.version
        
        with transaction.atomic():
            increment_versions(test_cart_with_item, cart_item)
        
        # Refresh from database
        test_cart_with_item.refresh_from_db()
        cart_item.refresh_from_db()
        
        assert test_cart_with_item.version == original_cart_version + 1
        assert cart_item.version == original_item_version + 1