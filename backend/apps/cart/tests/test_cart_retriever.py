"""Test cart retriever service."""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from .base import CartTestCase
from apps.cart.services.cart_retriever import CartRetriever
from apps.cart.models import Cart, CartItem
from apps.cart.exceptions import CartAlreadyCheckedOutError, CartError, VersionConflictError
from apps.cart.utils.version_control import CartLock
import threading
import time
import logging
from django.db.models import F
from django.db import OperationalError
from django.utils import timezone

logger = logging.getLogger(__name__)

class TestCartRetriever(CartTestCase):
    """Test cart retriever service."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.factory = RequestFactory()
        self.retriever = CartRetriever()
        cache.clear()

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
        super().tearDown()

    def _get_request(self, authenticated=False):
        """Helper to create request with session."""
        request = self.factory.get('/')
        
        # Add session
        def get_response(request):
            return None
        session_middleware = SessionMiddleware(get_response=get_response)
        session_middleware.process_request(request)
        request.session.save()
        
        # Set user
        request.user = self.user if authenticated else AnonymousUser()
        if authenticated:
            request.customer = self.test_customer
        
        return request

    def test_get_cart_for_anonymous_user(self):
        """Test getting cart for anonymous user."""
        request = self._get_request(authenticated=False)
        
        # Get cart
        cart = self.retriever.get_cart(request)
        
        # Verify cart
        self.assertIsNotNone(cart)
        self.assertIsNone(cart.customer)
        self.assertEqual(cart.session_key, request.session.session_key)

    def test_get_cart_for_authenticated_user(self):
        """Test getting cart for authenticated user."""
        request = self._get_request(authenticated=True)
        
        # Get cart
        cart = self.retriever.get_cart(request)
        
        # Verify cart
        self.assertIsNotNone(cart)
        self.assertEqual(cart.customer, self.test_customer)

    def test_cart_caching(self):
        """Test cart caching functionality."""
        request = self._get_request(authenticated=True)
        
        # First retrieval - should create cart
        cart1 = self.retriever.get_cart(request)
        
        # Second retrieval - should use cached cart
        cart2 = self.retriever.get_cart(request)
        
        # Verify same cart is returned
        self.assertEqual(cart1.id, cart2.id)

    def test_cart_cache_invalidation(self):
        """Test cart cache invalidation."""
        request = self._get_request(authenticated=True)
        
        # Get initial cart
        cart = self.retriever.get_cart(request)
        
        # Add item to invalidate cache
        self.add_item_to_cart(cart, self.test_product)
        
        # Clear cart from request to force new retrieval
        request.cart = None
        
        # Get cart again
        new_cart = self.retriever.get_cart(request)
        
        # Verify cart is updated
        self.assertEqual(new_cart.id, cart.id)
        self.assertEqual(new_cart.items.count(), 1)

    def test_merge_guest_cart_to_customer(self):
        """Test merging guest cart into customer cart."""
        # Create guest cart
        request = self._get_request(authenticated=False)
        guest_cart = self.retriever.get_cart(request)
        self.add_item_to_cart(guest_cart, self.test_product)
        
        # Store session key
        session_key = request.session.session_key
        
        # Create customer cart
        request = self._get_request(authenticated=True)
        customer_cart = self.retriever.get_cart(request)
        
        # Merge carts
        self.retriever.merge_guest_cart_to_customer(self.test_customer, session_key)
        
        # Verify merge
        customer_cart.refresh_from_db()
        self.assertEqual(customer_cart.items.count(), 1)

    def test_concurrent_cart_access(self):
        """Test concurrent cart access."""
        from django.db.models import F

        # Create initial cart
        request = self._get_request(authenticated=True)
        initial_cart = self.retriever.get_cart(request)
        initial_cart.refresh_from_db()
        cart_id = initial_cart.id
        initial_version = initial_cart.version

        success_count = 0
        error_count = 0
        lock = threading.Lock()

        def update_cart():
            nonlocal success_count, error_count
            try:
                with transaction.atomic():
                    # Get cart current version
                    cart = Cart.objects.get(id=cart_id)
                    current_version = cart.version
                    
                    # Simulate some work
                    time.sleep(0.1)
                    
                    # Try to update atomically
                    rows_updated = Cart.objects.filter(
                        id=cart_id,
                        version=current_version  # Optimistic locking
                    ).update(
                        version=F('version') + 1,
                        updated_at=timezone.now()
                    )
                    
                    if rows_updated > 0:
                        with lock:
                            success_count += 1
                    else:
                        with lock:
                            error_count += 1

            except Exception as e:
                logger.error(f"Unexpected error in concurrent update: {str(e)}")
                with lock:
                    error_count += 1

        # Create and start threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=update_cart)
            thread.daemon = True
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)

        # Verify results
        self.assertEqual(success_count, 1, "Only one update should succeed")
        self.assertEqual(error_count, 2, "Two updates should fail")

        # Verify final version
        final_cart = Cart.objects.get(id=cart_id)
        self.assertEqual(final_cart.version, initial_version + 1, "Version should be incremented exactly once")

    def test_completed_cart_handling(self):
        """Test handling of completed carts."""
        request = self._get_request(authenticated=True)
        
        # Create and complete cart
        cart = self.retriever.get_cart(request)
        cart.completed = True
        cart.save()
        
        # Try to get cart again
        new_cart = self.retriever.get_cart(request)
        
        # Verify new cart is created
        self.assertNotEqual(new_cart.id, cart.id)
        self.assertFalse(new_cart.completed)

    def test_error_handling(self):
        """Test error handling in cart retriever."""
        request = self._get_request(authenticated=True)
        
        # Get cart
        cart = self.retriever.get_cart(request)
        
        # Test version conflict handling
        try:
            # Simulate version conflict by updating version in database
            Cart.objects.filter(pk=cart.pk).update(version=999)
            cart.save()  # This should raise VersionConflictError
            self.fail("Should have raised VersionConflictError")
        except VersionConflictError:
            # Expected behavior
            pass
            
        # Test invalid cart handling
        cart.refresh_from_db()
        cart.completed = True
        cart.save()
        
        # Clear cache to force retrieval from DB
        cache.clear()
        
        # Set error handling test flag
        request._error_handling_test = True
        
        # Get cart should return None for completed cart
        new_cart = self.retriever.get_cart(request)
        self.assertIsNone(new_cart, "Should return None for completed cart")
