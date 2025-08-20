"""Test cart performance and load scenarios."""
from django.test import TransactionTestCase
from django.core.cache import cache
from django.test.client import RequestFactory
from django.db import connection
from .base import CartTestCase
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
import threading
import time
import random

class TestCartPerformance(CartTestCase):
    """Test cart performance under various conditions."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.factory = RequestFactory()
        cache.clear()
        # Create multiple test products
        self.test_products = []
        for i in range(10):
            product = Product.objects.create(
                name=f"Test Product {i}",
                description=f"Test Description {i}",
                category=self.test_category,
                price=10.00 + i,
                stock=100,
                available=True,
                status='active',
                version=1
            )
            self.test_products.append(product)

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
        super().tearDown()

    def test_bulk_cart_operations(self):
        """Test performance of bulk operations on cart."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Test bulk item addition
        items_to_add = []
        for product in self.test_products:
            items_to_add.append(CartItem(
                cart=cart,
                product=product,
                quantity=random.randint(1, 5)
            ))
        
        start_time = time.time()
        CartItem.objects.bulk_create(items_to_add)
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second
        self.assertEqual(cart.items.count(), len(self.test_products))

    def test_cart_retrieval_under_load(self):
        """Test cart retrieval performance under concurrent load."""
        cart = self.create_test_cart(customer=self.test_customer)
        for product in self.test_products[:5]:  # Add 5 items to cart
            self.add_item_to_cart(cart, product)

        def concurrent_read():
            """Concurrent read function."""
            connection.close()  # Ensure each thread gets its own connection
            cart.refresh_from_db()
            _ = cart.total_price
            _ = cart.items.all()

        # Create and run multiple threads
        threads = []
        for _ in range(10):  # Simulate 10 concurrent reads
            thread = threading.Thread(target=concurrent_read)
            threads.append(thread)
            thread.start()

        start_time = time.time()
        for thread in threads:
            thread.join()
        end_time = time.time()

        self.assertLess(end_time - start_time, 2.0)  # Should complete within 2 seconds

    def test_cart_updates_under_load(self):
        """Test cart update performance under concurrent load."""
        cart = self.create_test_cart(customer=self.test_customer)
        exceptions = []

        def concurrent_update(product_index):
            """Concurrent update function."""
            connection.close()
            try:
                cart.refresh_from_db()
                product = self.test_products[product_index]
                cart.add_item(product, random.randint(1, 3))
            except Exception as e:
                exceptions.append(e)

        # Create and run multiple threads
        threads = []
        for i in range(5):  # Try to add 5 different products concurrently
            thread = threading.Thread(target=concurrent_update, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(exceptions), 0)  # No exceptions should occur
        cart.refresh_from_db()
        self.assertGreater(cart.items.count(), 0)  # Items should be added
        self.assertLessEqual(cart.items.count(), 5)  # No more than 5 items

    def test_cart_calculation_performance(self):
        """Test performance of cart calculations with many items."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        # Add all test products with varying quantities
        for product in self.test_products:
            self.add_item_to_cart(cart, product, quantity=random.randint(1, 10))

        # Test calculation performance
        start_time = time.time()
        _ = cart.total_price
        _ = cart.total_items
        _ = cart.get_items_count()
        end_time = time.time()

        self.assertLess(end_time - start_time, 0.1)  # Calculations should be fast
