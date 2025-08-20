import pytest
import time
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.accounts.models import Customer
from django.test.utils import CaptureQueriesContext
from django.db import connection
import statistics

pytestmark = pytest.mark.django_db

class TestCartCachePerformance(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='1234567890'
        )
        self.products = []
        for i in range(10):
            self.products.append(Product.objects.create(
                name=f'Test Product {i}',
                price=Decimal(f'{10 + i}.00'),
                stock=10
            ))
        cache.clear()

    def test_cart_retrieval_caching(self):
        """Test performance improvement from cart caching."""
        self.client.force_login(self.user)
        
        # First request - should hit database
        with CaptureQueriesContext(connection) as first_context:
            start_time = time.time()
            response1 = self.client.get(reverse('cart:cart-detail'))
            first_request_time = time.time() - start_time
        
        # Second request - should hit cache
        with CaptureQueriesContext(connection) as second_context:
            start_time = time.time()
            response2 = self.client.get(reverse('cart:cart-detail'))
            second_request_time = time.time() - start_time
        
        # Verify cache hit reduces database queries
        assert len(first_context.captured_queries) > len(second_context.captured_queries)
        # Verify cache improves response time
        assert second_request_time < first_request_time

    def test_cart_item_bulk_operations(self):
        """Test performance of bulk cart operations with caching."""
        self.client.force_login(self.user)
        times = []
        
        # Add multiple items and measure performance
        for product in self.products:
            start_time = time.time()
            self.client.post(reverse('cart:add-to-cart'), {
                'product_id': str(product.id),
                'quantity': 1
            })
            times.append(time.time() - start_time)
        
        # Verify subsequent operations are faster due to caching
        assert statistics.mean(times[:3]) > statistics.mean(times[-3:])

    def test_cart_calculation_caching(self):
        """Test caching of cart calculations."""
        self.client.force_login(self.user)
        
        # Add items to cart
        for product in self.products[:5]:
            self.client.post(reverse('cart:add-to-cart'), {
                'product_id': str(product.id),
                'quantity': 1
            })
        
        # First calculation - should compute
        with CaptureQueriesContext(connection) as first_context:
            start_time = time.time()
            response1 = self.client.get(reverse('cart:cart-detail'))
            first_calc_time = time.time() - start_time
        
        # Second calculation - should use cache
        with CaptureQueriesContext(connection) as second_context:
            start_time = time.time()
            response2 = self.client.get(reverse('cart:cart-detail'))
            second_calc_time = time.time() - start_time
        
        # Verify calculations are cached
        assert len(first_context.captured_queries) > len(second_context.captured_queries)
        assert second_calc_time < first_calc_time

    def test_cache_invalidation_performance(self):
        """Test performance of cache invalidation after updates."""
        self.client.force_login(self.user)
        
        # Add item to cart
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.products[0].id),
            'quantity': 1
        })
        
        # Get cart from cache
        start_time = time.time()
        response1 = self.client.get(reverse('cart:cart-detail'))
        cached_time = time.time() - start_time
        
        # Update cart item
        self.client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': str(self.products[0].id)}),
            {'quantity': 2}
        )
        
        # Get cart after invalidation
        start_time = time.time()
        response2 = self.client.get(reverse('cart:cart-detail'))
        invalidated_time = time.time() - start_time
        
        # Verify cache was properly invalidated
        assert invalidated_time > cached_time

    def test_cache_memory_usage(self):
        """Test memory usage of cart caching."""
        self.client.force_login(self.user)
        initial_keys = len(cache._cache.keys())
        
        # Add items to cart
        for product in self.products:
            self.client.post(reverse('cart:add-to-cart'), {
                'product_id': str(product.id),
                'quantity': 1
            })
            self.client.get(reverse('cart:cart-detail'))
        
        # Verify reasonable cache key growth
        final_keys = len(cache._cache.keys())
        assert final_keys - initial_keys < 20  # Assuming reasonable cache key count

    def test_cache_hit_ratio(self):
        """Test cache hit ratio for cart operations."""
        self.client.force_login(self.user)
        cache_hits = 0
        total_requests = 100
        
        # Add item to cart
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.products[0].id),
            'quantity': 1
        })
        
        # Make multiple requests and count cache hits
        for _ in range(total_requests):
            with CaptureQueriesContext(connection) as context:
                self.client.get(reverse('cart:cart-detail'))
                if len(context.captured_queries) == 0:
                    cache_hits += 1
        
        # Verify high cache hit ratio
        hit_ratio = cache_hits / total_requests
        assert hit_ratio > 0.9  # Expect >90% cache hit ratio

    def test_cache_stampede_prevention(self):
        """Test prevention of cache stampede under load."""
        self.client.force_login(self.user)
        
        # Add items to cart
        for product in self.products[:5]:
            self.client.post(reverse('cart:add-to-cart'), {
                'product_id': str(product.id),
                'quantity': 1
            })
        
        # Simulate multiple simultaneous requests
        response_times = []
        for _ in range(10):
            start_time = time.time()
            self.client.get(reverse('cart:cart-detail'))
            response_times.append(time.time() - start_time)
        
        # Verify no significant performance degradation
        assert max(response_times) < 2 * min(response_times)

    def test_cache_consistency(self):
        """Test consistency of cached cart data."""
        self.client.force_login(self.user)
        
        # Add item to cart
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.products[0].id),
            'quantity': 1
        })
        
        # Get cart data from cache and database
        cache_response = self.client.get(reverse('cart:cart-detail'))
        cache.clear()  # Force database fetch
        db_response = self.client.get(reverse('cart:cart-detail'))
        
        # Verify data consistency
        assert cache_response.data == db_response.data