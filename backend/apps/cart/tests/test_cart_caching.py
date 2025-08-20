"""Test cart caching functionality."""
from django.test import TestCase, override_settings
from django.core.cache import cache
from decimal import Decimal
from .base import CartTestCase
from apps.cart.models import Cart
from django.test.client import RequestFactory
import threading
import time

class TestCartCaching(CartTestCase):
    """Test cart caching operations."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.factory = RequestFactory()
        cache.clear()

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
        super().tearDown()

    def test_cart_cache_hit(self):
        """Test cart is properly cached and retrieved."""
        # Create cart
        cart = self.create_test_cart(customer=self.test_customer)
        self.add_item_to_cart(cart, self.test_product)

        # Get cart through retriever (should cache it)
        request = self.factory.get('/')
        request.user = self.user
        request.customer = self.test_customer
        cached_cart = self.cart_retriever.get_cart(request)

        # Verify it's cached
        cache_key = self.cart_retriever._get_cache_key(f"user:{self.test_customer.id}")
        self.assertIsNotNone(cache.get(cache_key))

        # Get cart again (should hit cache)
        cached_cart_2 = self.cart_retriever.get_cart(request)
        self.assertEqual(cached_cart.id, cached_cart_2.id)

    def test_cache_invalidation_on_update(self):
        """Test cache is invalidated when cart is updated."""
        # Create and cache cart
        cart = self.create_test_cart(customer=self.test_customer)
        self.cart_retriever._cache_cart(str(self.test_customer.id), cart)

        # Update cart
        self.add_item_to_cart(cart, self.test_product)

        # Verify cache is invalidated
        cache_key = self.cart_retriever._get_cache_key(f"user:{self.test_customer.id}")
        cached_cart = cache.get(cache_key)
        self.assertIsNone(cached_cart)

    def test_concurrent_cache_access(self):
        """Test concurrent access to cached cart."""
        cart = self.create_test_cart(customer=self.test_customer)
        
        def concurrent_update():
            """Concurrent update function."""
            time.sleep(0.1)  # Simulate delay
            cart.add_item(self.test_product, 1)

        # Start concurrent update
        thread = threading.Thread(target=concurrent_update)
        thread.start()

        # Try to get cart while update is happening
        request = self.factory.get('/')
        request.user = self.user
        request.customer = self.test_customer
        retrieved_cart = self.cart_retriever.get_cart(request)

        # Wait for thread to finish
        thread.join()

        # Verify cart state
        self.assertIsNotNone(retrieved_cart)
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 1)

    @override_settings(CART_CACHE_TIMEOUT=1)
    def test_cache_expiration(self):
        """Test cart cache expiration."""
        # Create and cache cart
        cart = self.create_test_cart(customer=self.test_customer)
        self.cart_retriever._cache_cart(str(self.test_customer.id), cart)

        # Verify cart is cached
        cache_key = self.cart_retriever._get_cache_key(f"user:{self.test_customer.id}")
        self.assertIsNotNone(cache.get(cache_key))

        # Wait for cache to expire
        time.sleep(2)

        # Verify cart is no longer cached
        self.assertIsNone(cache.get(cache_key))

    def test_cache_clear_on_checkout(self):
        """Test cart cache is cleared after checkout."""
        # Create and cache cart
        cart = self.create_test_cart(customer=self.test_customer)
        self.cart_retriever._cache_cart(str(self.test_customer.id), cart)

        # Complete cart
        cart.completed = True
        cart.save()

        # Verify cache is cleared
        cache_key = self.cart_retriever._get_cache_key(f"user:{self.test_customer.id}")
        self.assertIsNone(cache.get(cache_key))

    def test_session_cart_caching(self):
        """Test caching for session carts."""
        session_key = 'test_session'
        cart = self.create_test_cart(session_key=session_key)

        # Cache cart
        self.cart_retriever._cache_cart(session_key, cart)

        # Verify it's cached
        cache_key = self.cart_retriever._get_cache_key(f"session:{session_key}")
        self.assertIsNotNone(cache.get(cache_key))

        # Clear cache
        self.cart_retriever.clear_cart_cache(session_key=session_key)

        # Verify it's cleared
        self.assertIsNone(cache.get(cache_key))
