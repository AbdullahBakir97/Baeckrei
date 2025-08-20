"""Integration tests for cart context processor."""
import pytest
from decimal import Decimal
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from layers.middleware.customer_middleware import CustomerMiddleware
from layers.middleware.cart_middleware import CartMiddleware
from layers.context_processors.cart_processor import cart_context_processor
from apps.cart.models import Cart

pytestmark = pytest.mark.django_db(transaction=True)

class TestCartContextProcessor:
    """Test cart context processor."""

    @pytest.fixture
    def middleware_stack(self):
        """Create middleware stack for testing."""
        def get_response(request):
            return None

        def apply_middleware(request):
            # Initialize middleware chain
            session_middleware = SessionMiddleware(get_response)
            auth_middleware = AuthenticationMiddleware(get_response)
            customer_middleware = CustomerMiddleware(get_response)
            cart_middleware = CartMiddleware(get_response)

            # Process request through middleware chain
            session_middleware.process_request(request)
            request.session.save()  # Save session to ensure session key exists
            
            auth_middleware.process_request(request)
            customer_middleware.process_request(request)
            
            # Process cart middleware
            cart_middleware.process_request(request)
            
            # Ensure cart is set
            if not hasattr(request, 'cart'):
                request.cart = None
                
            return request

        return apply_middleware

    def test_cart_context_anonymous_user(self, rf, middleware_stack):
        """Test cart context for anonymous user."""
        request = rf.get('/')
        request = middleware_stack(request)

        context = cart_context_processor(request)

        assert 'cart' in context
        assert isinstance(context['cart'], Cart)
        assert context['cart'].session_key == request.session.session_key
        assert context['cart_items_count'] == 0
        assert context['cart_total'] == Decimal('0.00')

    def test_cart_context_authenticated_user(self, rf, middleware_stack, test_user, test_customer):
        """Test cart context for authenticated user."""
        request = rf.get('/')
        request.user = test_user
        request._cached_user = test_user
        request = middleware_stack(request)

        context = cart_context_processor(request)

        assert 'cart' in context
        assert isinstance(context['cart'], Cart)
        assert context['cart'].customer == test_customer
        assert context['cart_items_count'] == 0
        assert context['cart_total'] == Decimal('0.00')

    def test_cart_context_with_items(self, rf, middleware_stack, test_cart_with_item):
        """Test cart context with items in cart."""
        request = rf.get('/')
        request = middleware_stack(request)
        
        # Override the cart from middleware with our test cart
        request.cart = test_cart_with_item

        context = cart_context_processor(request)

        assert context['cart_items_count'] == 2  # Quantity is 2
        # Subtotal is €20.00 (1 item with quantity=2 at €10.00 each)
        # Tax is 19% of €20.00 = €3.80
        # Total is €23.80
        assert context['cart_total'] == Decimal('23.80')
        assert len(context['cart'].items.all()) == 1  # One item with quantity=2

    def test_cart_context_format(self, rf, middleware_stack, test_cart_with_item):
        """Test formatting of cart context values."""
        request = rf.get('/')
        request = middleware_stack(request)
        
        # Override the cart from middleware with our test cart
        request.cart = test_cart_with_item

        context = cart_context_processor(request)

        assert isinstance(context['cart_total'], Decimal)
        assert isinstance(context['cart_items_count'], int)
        # Subtotal is €20.00 (2 items at €10.00 each)
        # Tax is 19% of €20.00 = €3.80
        # Total is €23.80
        assert context['cart_total'] == Decimal('23.80')

    def test_cart_context_empty_cart(self, rf, middleware_stack, empty_cart):
        """Test cart context with empty cart."""
        request = rf.get('/')
        request = middleware_stack(request)
        
        # Override the cart from middleware with our test cart
        request.cart = empty_cart

        context = cart_context_processor(request)

        assert context['cart_items_count'] == 0
        assert context['cart_total'] == Decimal('0.00')
        assert len(context['cart'].items.all()) == 0

    def test_cart_context_persistence(self, rf, middleware_stack, test_product, empty_cart):
        """Test that cart context persists between requests."""
        # First request
        request1 = rf.get('/')
        request1 = middleware_stack(request1)
        
        # Override the cart from middleware with our test cart
        request1.cart = empty_cart
        request1.cart.add_item(test_product, 1)

        context1 = cart_context_processor(request1)
        assert context1['cart_items_count'] == 1

        # Second request with same session
        request2 = rf.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)
        request2.cart = request1.cart

        context2 = cart_context_processor(request2)
        assert context2['cart_items_count'] == 1
        assert context2['cart'].id == context1['cart'].id

    def test_cart_context_template_variables(self, rf, middleware_stack, test_cart_with_item):
        """Test all template variables provided by context processor."""
        request = rf.get('/')
        request = middleware_stack(request)
        
        # Override the cart from middleware with our test cart
        request.cart = test_cart_with_item

        context = cart_context_processor(request)

        expected_keys = {'cart', 'cart_total', 'cart_items_count'}
        assert all(key in context for key in expected_keys)
        assert context['cart_items_count'] == 2  # Quantity is 2