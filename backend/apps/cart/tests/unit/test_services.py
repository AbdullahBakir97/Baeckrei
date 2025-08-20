import pytest
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.db import transaction
from apps.cart.services import CartService
from apps.cart.exceptions import (
    CartException,
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError,
    VersionConflict
)
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from django.core.exceptions import ValidationError

class TestCartService(TestCase):
    def setUp(self):
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            category=self.category,
            price=Decimal('10.00'),
            stock=10,
            available=True,
            status='active'
        )
        
        # Create test cart
        self.cart = Cart.objects.create()
        self.cart_service = CartService(self.cart)

    def test_add_item_to_cart(self):
        """Test adding an item to the cart."""
        result = self.cart_service.add_item(self.product.id, 2)

        # Verify cart state
        cart_item = self.cart.items.first()
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.unit_price, self.product.price)

        # Verify product stock was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # Verify response format
        self.assertEqual(result['status'], 'success')
        self.assertIn('cart', result['data'])
        cart_data = result['data']['cart']
        
        # Verify cart items
        self.assertIn('items', cart_data)
        self.assertEqual(len(cart_data['items']), 1)
        item = cart_data['items'][0]
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(item['name'], self.product.name)
        self.assertEqual(item['unit_price'], '€10,00')

    def test_add_item_exceeding_stock(self):
        """Test adding item with quantity exceeding stock."""
        with self.assertRaises(CartException) as cm:
            self.cart_service.add_item(self.product.id, self.product.stock + 1)
        self.assertIn("Not enough stock", str(cm.exception))
        
        # Verify stock wasn't modified
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_remove_item_from_cart(self):
        """Test removing an item from the cart."""
        # Store initial stock
        initial_stock = self.product.stock  # Should be 10
        
        # Add an item
        self.cart_service.add_item(self.product.id, 2)  # Stock becomes 8
        self.cart.refresh_from_db()
        
        # Create new service with updated cart
        updated_service = CartService(self.cart)
        
        # Then remove it
        result = updated_service.remove_item(self.product.id)  # Stock should return to 10
        
        # Verify item was removed
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock)
        self.assertEqual(len(result['data']['cart']['items']), 0)

    def test_update_item_quantity(self):
        """Test updating item quantity."""
        # Add initial item
        self.cart_service.add_item(self.product.id, 2)
        self.cart.refresh_from_db()
        
        # Create new service with updated cart
        updated_service = CartService(self.cart)
        
        # Update quantity
        result = updated_service.update_item(self.product.id, 3)
        
        # Verify quantity was updated
        self.assertEqual(result['data']['cart']['items'][0]['quantity'], 3)
        self.assertEqual(len(result['data']['cart']['items']), 1)

    def test_clear_cart(self):
        """Test clearing the cart."""
        # Store initial stock before adding items
        initial_stock = self.product.stock
        
        # Add some items
        self.cart_service.add_item(self.product.id, 2)
        self.cart.refresh_from_db()
        
        # Create new service with updated cart
        updated_service = CartService(self.cart)
        
        # Clear cart
        result = updated_service.clear_cart()
        
        # Verify cart was cleared
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock)
        self.assertEqual(len(result['data']['cart']['items']), 0)

    def test_cart_total_calculation(self):
        """Test cart total calculation."""
        # Add items
        self.cart_service.add_item(self.product.id, 2)

        # Calculate expected total (subtotal + 19% tax)
        subtotal = self.product.price * 2
        tax = subtotal * Decimal('0.19')
        expected_total = subtotal + tax

        # Verify total
        self.assertEqual(self.cart_service.total_price, expected_total)

    def test_cart_item_count(self):
        """Test cart item count."""
        # Add items
        self.cart_service.add_item(self.product.id, 2)
        
        # Verify count
        self.assertEqual(self.cart_service.item_count, 2)

    def test_completed_cart_operations(self):
        """Test operations on completed cart."""
        # Complete the cart
        self.cart.completed = True
        self.cart.save()
        
        # Attempt operations on completed cart
        with self.assertRaises(CartAlreadyCheckedOutError):
            CartService(self.cart)

    def test_invalid_product(self):
        """Test operations with invalid product ID."""
        with self.assertRaises(CartException):
            try:
                self.cart_service.add_item('invalid-id')
            except ValidationError as e:
                raise CartException(str(e))

    def test_invalid_quantity(self):
        """Test operations with invalid quantity."""
        with self.assertRaises(CartException):
            try:
                self.cart_service.add_item(self.product.id, 0)
            except ValidationError as e:
                raise CartException(str(e))

    def test_version_control(self):
        """Test version control during concurrent operations."""
        # Add item to increment version
        self.cart_service.add_item(self.product.id, 1)
        self.cart.refresh_from_db()
        initial_version = self.cart.version
        
        # Create another service instance with old version
        stale_cart = Cart.objects.get(id=self.cart.id)
        stale_cart.version = initial_version - 1  # Force old version
        old_service = CartService(stale_cart)
        
        # Update with old service should fail
        with self.assertRaises(VersionConflict):
            old_service.update_item(self.product.id, 3)
        
        # Create new service with latest cart
        fresh_cart = Cart.objects.get(id=self.cart.id)
        new_service = CartService(fresh_cart)
        
        # Update with new service should succeed
        result = new_service.update_item(self.product.id, 2)
        
        # Verify version was incremented
        self.cart.refresh_from_db()
        self.assertGreater(self.cart.version, initial_version)

    def test_cart_data_formatting(self):
        """Test cart data formatting."""
        # Add item
        result = self.cart_service.add_item(self.product.id, 2)

        # Verify data structure and formatting
        data = result['data']
        cart_data = data['cart']
        
        # Check cart structure
        self.assertIn('items', cart_data)
        self.assertIn('total_items', cart_data)
        self.assertIn('subtotal', cart_data)
        self.assertIn('tax', cart_data)
        self.assertIn('total', cart_data)
        
        # Check items data
        items = cart_data['items']
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item['quantity'], 2)
        self.assertEqual(item['name'], self.product.name)
        self.assertEqual(item['unit_price'], '€10,00')
        self.assertEqual(item['subtotal'], '€20,00')
        
        # Check cart totals
        self.assertEqual(cart_data['total_items'], 2)
        self.assertEqual(cart_data['subtotal'], '€20,00')
        self.assertEqual(cart_data['tax'], '€3,80')  # 19% VAT
        self.assertEqual(cart_data['total'], '€23,80')

    def test_concurrent_stock_updates(self):
        """Test handling of concurrent stock updates."""
        with transaction.atomic():
            # Add item to cart
            self.cart_service.add_item(self.product.id, 2)
            
            # Update product stock directly
            Product.objects.filter(id=self.product.id).update(stock=5)
            
            # Attempt to add more items
            with self.assertRaises(CartException):
                self.cart_service.add_item(self.product.id, 4)  # Would exceed new stock
                
        # Verify final stock
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)