"""Test cart edge cases and boundary conditions."""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import override_settings
from .base import CartTestCase
from apps.cart.models import Cart, CartItem
from apps.cart.exceptions import InsufficientStockError, CartError
from apps.products.models import Product

class TestCartEdgeCases(CartTestCase):
    """Test edge cases in cart operations."""

    def test_maximum_quantity(self):
        """Test adding maximum possible quantity."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Try to add more than available stock
        with self.assertRaises(InsufficientStockError):
            self.add_item_to_cart(cart, self.test_product, self.test_product.stock + 1)

        # Add exactly available stock
        cart_item = self.add_item_to_cart(cart, self.test_product, self.test_product.stock)
        self.assertEqual(cart_item.quantity, self.test_product.stock)

    def test_minimum_quantity(self):
        """Test edge cases with minimum quantities."""
        cart = self.create_test_cart(customer=self.test_customer)

        # Try to add zero quantity
        with self.assertRaises(ValidationError):
            self.add_item_to_cart(cart, self.test_product, 0)

        # Try to add negative quantity
        with self.assertRaises(ValidationError):
            self.add_item_to_cart(cart, self.test_product, -1)

    def test_deleted_product(self):
        """Test handling of deleted products."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add item then delete product
        cart_item = self.add_item_to_cart(cart, self.test_product)
        self.test_product.delete()

        # Refresh cart item and verify it's handled gracefully
        cart_item.refresh_from_db()
        self.assertIsNone(cart_item.product)

    def test_price_changes(self):
        """Test handling of price changes during operations."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add item
        cart_item = self.add_item_to_cart(cart, self.test_product)
        original_price = cart_item.unit_price

        # Change product price
        self.test_product.price = Decimal('15.00')
        self.test_product.save()

        # Add more of same item
        cart_item = self.add_item_to_cart(cart, self.test_product)
        
        # Verify price was updated
        self.assertNotEqual(cart_item.unit_price, original_price)
        self.assertEqual(cart_item.unit_price, Decimal('15.00'))

    def test_cart_with_unavailable_product(self):
        """Test cart behavior with unavailable products."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add item then make product unavailable
        cart_item = self.add_item_to_cart(cart, self.test_product)
        self.test_product.available = False
        self.test_product.save()

        # Try to add more of unavailable product
        with self.assertRaises(CartError):
            self.add_item_to_cart(cart, self.test_product)

    def test_multiple_cart_items_same_product(self):
        """Test preventing multiple cart items for same product."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add item twice
        self.add_item_to_cart(cart, self.test_product, 1)
        self.add_item_to_cart(cart, self.test_product, 2)

        # Verify only one cart item exists with combined quantity
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 3)

    def test_cart_item_price_precision(self):
        """Test handling of price precision."""
        # Create product with many decimal places
        product = Product.objects.create(
            name='Precise Product',
            price=Decimal('10.12345'),
            stock=10,
            available=True,
            status='active'
        )

        cart = self.create_test_cart(customer=self.test_customer)
        cart_item = self.add_item_to_cart(cart, product)

        # Verify price is rounded correctly
        self.assertEqual(cart_item.unit_price, Decimal('10.12'))

    def test_cart_item_overflow(self):
        """Test handling of quantity overflow scenarios."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Try to add quantity that would overflow integer field
        max_int = 2147483647  # Max value for PostgreSQL integer
        with self.assertRaises(ValidationError):
            self.add_item_to_cart(cart, self.test_product, max_int + 1)

    def test_multiple_cart_items_same_product(self):
        """Test handling of multiple cart items for the same product."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add same product multiple times
        self.add_item_to_cart(cart, self.test_product, 1)
        self.add_item_to_cart(cart, self.test_product, 2)
        
        # Verify only one cart item exists with combined quantity
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 3)

    def test_cart_item_price_precision(self):
        """Test handling of price precision and rounding."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Create product with fractional price
        product = Product.objects.create(
            name="Fractional Price Product",
            description="Test Description",
            category=self.test_category,
            price=9.99,
            stock=10,
            available=True,
            status='active',
            version=1
        )
        
        # Add multiple items and check total price precision
        cart_item = self.add_item_to_cart(cart, product, 3)
        expected_total = Decimal('29.97')  # 9.99 * 3
        self.assertEqual(cart_item.total_price, expected_total)

    def test_cart_cleanup(self):
        """Test cleanup of empty carts."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add and then remove item
        cart_item = self.add_item_to_cart(cart, self.test_product)
        cart_item.delete()
        
        # Verify cart still exists but is empty
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0)
        
        # Verify cart can still be used
        new_item = self.add_item_to_cart(cart, self.test_product)
        self.assertEqual(cart.items.count(), 1)

    @override_settings(CART_MAX_ITEMS=5)
    def test_cart_item_limit(self):
        """Test cart item limit."""
        cart = self.create_test_cart(customer=self.test_customer)

        # Add items up to limit
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}',
                price=Decimal('10.00'),
                stock=10,
                available=True,
                status='active'
            )
            self.add_item_to_cart(cart, product)

        # Try to add one more
        product = Product.objects.create(
            name='Extra Product',
            price=Decimal('10.00'),
            stock=10,
            available=True,
            status='active'
        )
        
        with self.assertRaises(ValidationError):
            self.add_item_to_cart(cart, product)

    def test_cart_total_overflow(self):
        """Test handling of very large cart totals."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Create expensive product
        expensive_product = Product.objects.create(
            name='Expensive Product',
            price=Decimal('9999999.99'),
            stock=10,
            available=True,
            status='active'
        )

        # Add maximum quantity
        cart_item = self.add_item_to_cart(cart, expensive_product, 10)
        
        # Verify total is calculated correctly
        self.assertEqual(cart.total, Decimal('99999999.90'))

    def test_unicode_product_names(self):
        """Test handling of unicode product names."""
        # Create product with unicode name
        unicode_product = Product.objects.create(
            name='测试产品',  # Chinese characters
            price=Decimal('10.00'),
            stock=10,
            available=True,
            status='active'
        )

        cart = self.create_test_cart(customer=self.test_customer)
        cart_item = self.add_item_to_cart(cart, unicode_product)
        
        # Verify unicode handling
        self.assertEqual(str(cart_item), f"1x 测试产品 in Cart {cart.id}")

    def test_concurrent_cart_deletion(self):
        """Test handling of concurrent cart deletion."""
        cart = self.create_test_cart(customer=self.test_customer)
        self.add_item_to_cart(cart, self.test_product)

        with transaction.atomic():
            # Delete cart concurrently
            Cart.objects.filter(pk=cart.pk).delete()
            
            # Try to add item to deleted cart
            with self.assertRaises(Cart.DoesNotExist):
                self.add_item_to_cart(cart, self.test_product)
