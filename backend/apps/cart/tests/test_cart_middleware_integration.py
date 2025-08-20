"""Test cart middleware and processor integration."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from decimal import Decimal
from .base import CartTestCase
from layers.middleware.cart_middleware import CartMiddleware
from layers.context_processors.cart_processor import cart_context_processor
from apps.cart.models import Cart
from apps.cart.commands.cart_commands import ValidateCartCommand
from django.utils import timezone

class TestCartMiddlewareIntegration(CartTestCase):
    """Test cart middleware integration with context processor."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.factory = RequestFactory()
        self.middleware = CartMiddleware(get_response=lambda x: x)
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

    def test_anonymous_user_cart_creation(self):
        """Test cart creation for anonymous user."""
        request = self._get_request(authenticated=False)
        
        # Process request
        self.middleware.process_request(request)
        
        # Verify cart was created and attached
        self.assertIsNotNone(request.cart)
        self.assertIsNone(request.cart.customer)
        self.assertEqual(request.cart.session_key, request.session.session_key)

    def test_authenticated_user_cart_creation(self):
        """Test cart creation for authenticated user."""
        request = self._get_request(authenticated=True)
        
        # Process request
        self.middleware.process_request(request)
        
        # Verify cart was created and attached
        self.assertIsNotNone(request.cart)
        self.assertEqual(request.cart.customer, self.test_customer)

    def test_cart_context_processor_empty_cart(self):
        """Test context processor with empty cart."""
        request = self._get_request(authenticated=True)
        request.cart = None
        
        # Get context
        context = cart_context_processor(request)
        
        # Verify empty cart context
        self.assertIsNone(context['cart'])
        self.assertEqual(context['cart_total'], Decimal('0.00'))
        self.assertEqual(context['cart_items_count'], 0)

    def test_cart_context_processor_with_items(self):
        """Test context processor with cart containing items."""
        request = self._get_request(authenticated=True)
        
        # Create cart with items
        cart = self.create_test_cart(customer=self.test_customer)
        self.add_item_to_cart(cart, self.test_product, quantity=2)
        request.cart = cart
        
        # Get context
        context = cart_context_processor(request)
        
        # Verify context with items
        self.assertEqual(context['cart'], cart)
        self.assertEqual(context['cart_total'], cart.total)
        self.assertEqual(context['cart_items_count'], cart.total_items)

    def test_cart_validation_in_context_processor(self):
        """Test cart validation in context processor."""
        request = self._get_request(authenticated=True)
        
        # Create cart with invalid state
        cart = self.create_test_cart(customer=self.test_customer)
        cart.completed = True
        cart.completed_at = timezone.now()
        cart.save()
        request.cart = cart
        
        # Process request through middleware first
        self.middleware.process_request(request)
        
        # Get context
        context = cart_context_processor(request)
        
        # Verify context - should create a new cart since old one is completed
        self.assertIsNotNone(context['cart'])
        self.assertNotEqual(context['cart'].id, cart.id)
        self.assertEqual(context['cart_total'], Decimal('0.00'))
        self.assertEqual(context['cart_items_count'], 0)

    def test_cart_middleware_caching(self):
        """Test cart caching in middleware."""
        request = self._get_request(authenticated=True)
        
        # First request - should create cart
        self.middleware.process_request(request)
        original_cart_id = request.cart.id
        
        # Verify cart is cached
        cache_key = f"cart:user:{self.test_customer.id}"
        cached_cart = cache.get(cache_key)
        self.assertIsNotNone(cached_cart)
        self.assertEqual(cached_cart.id, original_cart_id)
        
        # Second request - should use cached cart
        new_request = self._get_request(authenticated=True)
        self.middleware.process_request(new_request)
        
        # Verify same cart is used
        self.assertEqual(new_request.cart.id, original_cart_id)
        
        # Modify cart to test cache invalidation
        request.cart.completed = True
        request.cart.save()
        cache.delete(cache_key)  # Simulate cache invalidation
        
        # Third request - should create new cart
        final_request = self._get_request(authenticated=True)
        self.middleware.process_request(final_request)
        
        # Verify new cart was created
        self.assertNotEqual(final_request.cart.id, original_cart_id)
        self.assertFalse(final_request.cart.completed)

    def test_cart_middleware_admin_urls(self):
        """Test middleware skips admin URLs."""
        request = self.factory.get('/admin/some/path')
        request.user = self.user
        
        # Process admin URL request
        result = self.middleware.process_request(request)
        
        # Verify middleware was skipped
        self.assertIsNone(result)
        self.assertFalse(hasattr(request, 'cart'))

    def test_cart_middleware_static_urls(self):
        """Test middleware skips static URLs."""
        request = self.factory.get('/static/some/path')
        request.user = self.user
        
        # Process static URL request
        result = self.middleware.process_request(request)
        
        # Verify middleware was skipped
        self.assertIsNone(result)
        self.assertFalse(hasattr(request, 'cart'))
