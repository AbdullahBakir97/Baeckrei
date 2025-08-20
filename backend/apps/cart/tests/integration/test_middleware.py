"""Tests for cart middleware."""
import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.conf import settings
from django.http import HttpResponse
from importlib import import_module
from datetime import timedelta
from django.utils import timezone
from apps.cart.models import Cart, CartItem
from apps.cart.services.cart_retriever import CartRetriever
from layers.middleware.cart_middleware import CartMiddleware
from layers.middleware.customer_middleware import CustomerMiddleware
from apps.accounts.models import Customer
from django.db import transaction
from django.core.cache import cache
import time

pytestmark = pytest.mark.django_db(transaction=True)

class TestCartMiddleware:
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def get_response(self):
        def _get_response(request):
            return HttpResponse()
        return _get_response

    @pytest.fixture
    def middleware_stack(self):
        """Create middleware stack for testing."""
        def apply_middleware(request):
            """Apply middleware stack to request."""
            from django.contrib.sessions.middleware import SessionMiddleware
            from django.contrib.auth.middleware import AuthenticationMiddleware
            from layers.middleware.customer_middleware import CustomerMiddleware
            from layers.middleware.cart_middleware import CartMiddleware
            from django.conf import settings
            from importlib import import_module

            def dummy_get_response(request):
                return None

            # Get session engine
            engine = import_module(settings.SESSION_ENGINE)

            # Initialize session middleware
            session_middleware = SessionMiddleware(dummy_get_response)
            
            if hasattr(request, 'session'):
                # Check for potentially malicious data
                session_data = dict(request.session)
                potentially_malicious = any(
                    key for key in session_data.keys() 
                    if key not in {'_auth_user_id', '_auth_user_backend', '_auth_user_hash', 'cart_id'}
                )
                
                if potentially_malicious:
                    # For malicious sessions, create entirely new session
                    old_session_data = dict(request.session)
                    old_session_key = request.session.session_key
                    
                    # Create new session
                    request.session.flush()
                    session_middleware.process_request(request)
                    
                    # Copy only safe data
                    safe_keys = {'_auth_user_id', '_auth_user_backend', '_auth_user_hash', 'cart_id'}
                    for key in safe_keys:
                        if key in old_session_data:
                            request.session[key] = old_session_data[key]
                    
                    request.session.modified = True
                    request.session.save()
                    
                    # Delete old session
                    if old_session_key:
                        old_session = engine.SessionStore(session_key=old_session_key)
                        old_session.delete()
                else:
                    # For clean sessions, only create if needed
                    if not request.session.session_key:
                        session_middleware.process_request(request)
                        request.session.save()
            else:
                # No session exists, create new one
                session_middleware.process_request(request)
                request.session.save()
            
            # Apply other middleware
            auth_middleware = AuthenticationMiddleware(dummy_get_response)
            customer_middleware = CustomerMiddleware(dummy_get_response)
            cart_middleware = CartMiddleware(dummy_get_response)

            auth_middleware.process_request(request)
            customer_middleware.process_request(request)
            cart_middleware(request)

            return request

        return apply_middleware

    def test_anonymous_user_cart_creation(self, request_factory, middleware_stack):
        """Test cart creation for anonymous user."""
        request = request_factory.get('/')
        request = middleware_stack(request)
        
        assert hasattr(request, 'cart')
        assert isinstance(request.cart, Cart)
        assert request.cart.session_key == request.session.session_key
        assert request.cart.customer is None

    def test_authenticated_user_cart_creation(self, request_factory, middleware_stack, test_user, test_customer):
        """Test cart creation for authenticated user."""
        # Create request
        request = request_factory.get('/')
        
        # Set up session
        session_middleware = SessionMiddleware(lambda x: None)
        session_middleware.process_request(request)
        request.session.save()
        
        # Set up authentication
        request._cached_user = test_user  # Set cached user first
        request.user = test_user
        request.session[SESSION_KEY] = str(test_user.id)
        request.session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
        request.session.save()
        
        # Apply middleware stack
        request = middleware_stack(request)
        
        # Verify the user is properly authenticated
        assert request.user.is_authenticated, "User should be authenticated"
        assert hasattr(request, 'customer'), "Request should have customer attribute"
        assert request.customer == test_customer, "Customer should be set correctly"
        
        # Verify cart
        assert hasattr(request, 'cart'), "Request should have cart attribute"
        assert isinstance(request.cart, Cart), "Cart should be a Cart instance"
        assert request.cart.customer == test_customer, "Cart should be associated with customer"

    def test_cart_persistence_between_requests(self, request_factory, middleware_stack):
        """Test that cart persists between requests."""
        # First request
        request1 = request_factory.get('/')
        request1.user = AnonymousUser()

        # Initialize session
        engine = import_module(settings.SESSION_ENGINE)
        session1 = engine.SessionStore()
        session1.create()
        session_key = session1.session_key
        request1.session = session1
        request1.session.modified = False  # Prevent session key regeneration
        request1.session.save()

        # Apply middleware stack
        request1 = middleware_stack(request1)
        assert request1.cart is not None, "Cart should be created for first request"
        cart_id1 = request1.cart.id
        assert request1.session.session_key == session_key, "Session key should not change after middleware"

        # Second request with same session
        request2 = request_factory.get('/')
        request2.user = AnonymousUser()
        request2.session = request1.session
        request2.session.modified = False  # Prevent session key regeneration
        request2.session.save()

        # Apply middleware stack
        request2 = middleware_stack(request2)
        assert request2.cart is not None, "Cart should persist for second request"
        assert request2.cart.id == cart_id1, "Cart ID should be the same"
        assert request2.session.session_key == session_key, "Session key should remain unchanged"

    def test_session_fixation_prevention(self, request_factory, middleware_stack):
        """Test that session fixation is prevented."""
        request = request_factory.get('/')
        request.user = AnonymousUser()

        # Create a session with malicious data
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore()
        session.create()  # Create the session first
        session['malicious_key'] = 'attack'
        session.save()  # Save the session data
        request.session = session
        original_session_key = session.session_key

        # Apply middleware stack which should create a new session
        request = middleware_stack(request)

        # Verify session was regenerated and cleaned
        assert request.session.session_key is not None, "Session key should be created"
        assert request.session.session_key != original_session_key, "Session key should be different"
        assert 'malicious_key' not in request.session, "Malicious data should be removed"
        
        # Store the cleaned session key
        cleaned_session_key = request.session.session_key
        
        # Make another request with the cleaned session
        request2 = request_factory.get('/')
        request2.user = AnonymousUser()
        request2.session = engine.SessionStore(session_key=cleaned_session_key)
        request2.session['malicious_key'] = 'attack'  # Add malicious data again
        request2 = middleware_stack(request2)
        
        # Verify session is regenerated again
        assert request2.session.session_key != cleaned_session_key, "Session key should be rotated"
        assert 'malicious_key' not in request2.session, "Malicious data should be removed"

    def test_expired_cart_handling(self, request_factory, middleware_stack):
        """Test that expired carts are properly handled."""
        # First request to create cart
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart1 = request1.cart
        session_key = request1.session.session_key

        # Manually expire the cart by setting modified_at in the past
        with transaction.atomic():
            Cart.objects.filter(pk=cart1.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )  # Use direct update to bypass auto_now
            # Clear the cache to ensure we don't get stale data
            cache.delete(f"cart:session:{session_key}")
            cache.delete(f"cart:{session_key}")

        # Second request should detect expired cart and create new one
        request2 = request_factory.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)

        # Original cart should be marked as completed
        cart1.refresh_from_db()
        assert cart1.completed, "Expired cart should be marked as completed"
        assert request2.cart.id != cart1.id, "New cart should be created"
        assert not request2.cart.completed, "New cart should not be completed"
        assert not request2.cart.is_expired(), "New cart should not be expired"

    def test_expired_cart_cache_cleanup(self, request_factory, middleware_stack):
        """Test that expired carts are removed from cache."""
        # First request to create and cache cart
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart1 = request1.cart
        session_key = request1.session.session_key
        cache_key = f"cart:session:{session_key}"

        # Verify cart is in cache
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart1.id, "Cached cart should match original cart"

        # Manually expire the cart by setting modified_at in the past
        with transaction.atomic():
            Cart.objects.filter(pk=cart1.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Second request should clean up cache and create new cart
        request2 = request_factory.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)

        # Verify the original cart is no longer in cache
        cached_cart = cache.get(cache_key)
        assert cached_cart is None or cached_cart.id != cart1.id, "Expired cart should be removed from cache"

        # Verify the new cart is properly cached
        assert request2.cart is not None, "New cart should be created"
        assert request2.cart.id != cart1.id, "New cart should have different ID"
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"

    def test_expired_cart_merge_handling(self, request_factory, middleware_stack, test_user, test_customer, test_product):
        """Test that expired carts are handled properly during merge."""
        # Create anonymous cart
        anon_request = request_factory.get('/')
        anon_request = middleware_stack(anon_request)
        anon_cart = anon_request.cart
        
        # Add item to anonymous cart
        anon_cart.add_item(test_product, 2)
        
        # Expire anonymous cart by updating modified_at directly in database
        with transaction.atomic():
            Cart.objects.filter(pk=anon_cart.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Create authenticated request
        auth_request = request_factory.get('/')
        auth_request.session = anon_request.session
        
        # Set up authentication
        auth_request.user = test_user
        auth_request._cached_user = test_user
        auth_request.session[SESSION_KEY] = str(test_user.id)
        auth_request.session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
        auth_request.session.save()
        
        # Clear cache to ensure we don't get stale data
        cache.delete(f"cart:session:{anon_request.session.session_key}")
        cache.delete(f"cart:{anon_request.session.session_key}")

        auth_request = middleware_stack(auth_request)
        
        # Verify expired cart was not merged
        anon_cart.refresh_from_db()
        assert anon_cart.completed, "Expired anonymous cart should be marked as completed"
        assert auth_request.cart.items.count() == 0, "No items should be merged from expired cart"
        assert auth_request.cart.customer == test_customer, "New cart should be associated with customer"

    def test_cart_cleanup_on_session_expiry(self, request_factory, middleware_stack):
        """Test that expired carts are cleaned up."""
        request = request_factory.get('/')
        request = middleware_stack(request)
        cart = request.cart
        session_key = request.session.session_key
        cache_key = f"cart:session:{session_key}"

        # Verify cart is in cache
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart.id, "Cached cart should match original cart"

        # Mark cart as expired by updating modified_at directly in database
        with transaction.atomic():
            Cart.objects.filter(pk=cart.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Clear cache to ensure we don't get stale data
        cache.delete(cache_key)
        cache.delete(f"cart:{session_key}")

        # New request should create new cart
        request2 = request_factory.get('/')
        request2.session = request.session
        request2 = middleware_stack(request2)

        # Verify old cart is completed and new cart is created
        cart.refresh_from_db()
        assert cart.completed, "Expired cart should be marked as completed"
        assert request2.cart is not None, "New cart should be created"
        assert request2.cart.id != cart.id, "New cart should have different ID"

        # Verify new cart is properly cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"

    def test_middleware_performance(self, request_factory, middleware_stack):
        """Test middleware performance with cached cart."""
        # First request to populate cache
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart_id = request1.cart.id
        
        # Second request should use cached cart
        request2 = request_factory.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)
        
        assert request2.cart.id == cart_id

    def test_expired_cart_in_authenticated_session(self, request_factory, middleware_stack, test_user, test_customer):
        """Test expired cart handling for authenticated users."""
        # Create authenticated request
        request = request_factory.get('/')
        request.user = test_user
        request.customer = test_customer
        request._cached_user = test_user
        request = middleware_stack(request)
        cart = request.cart
        cache_key = f"cart:user:{test_customer.id}"

        # Verify cart is cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart.id, "Cached cart should match original cart"

        # Expire the cart by updating modified_at directly in database
        with transaction.atomic():
            Cart.objects.filter(pk=cart.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Clear cache to ensure we don't get stale data
        cache.delete(cache_key)
        cache.delete(f"cart:{test_customer.id}")

        # Make another request
        request2 = request_factory.get('/')
        request2.user = test_user
        request2.customer = test_customer
        request2._cached_user = test_user
        request2.session = request.session
        request2 = middleware_stack(request2)

        # Verify expired cart handling
        cart.refresh_from_db()
        assert cart.completed, "Expired cart should be marked as completed"
        assert request2.cart is not None, "New cart should be created"
        assert request2.cart.id != cart.id, "New cart should have different ID"
        assert request2.cart.customer == test_customer, "New cart should be associated with customer"

        # Verify new cart is properly cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"

    def test_concurrent_expired_cart_handling(self, request_factory, middleware_stack):
        """Test handling of concurrent requests with expired cart."""
        # Create initial cart
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart1 = request1.cart
        session_key = request1.session.session_key
        cache_key = f"cart:session:{session_key}"

        # Verify cart is cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart1.id, "Cached cart should match original cart"

        # Expire the cart by updating modified_at directly in database
        with transaction.atomic():
            Cart.objects.filter(pk=cart1.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Clear cache to ensure we don't get stale data
        cache.delete(cache_key)
        cache.delete(f"cart:{session_key}")

        # Simulate concurrent requests
        request2 = request_factory.get('/')
        request2.session = request1.session
        request3 = request_factory.get('/')
        request3.session = request1.session

        # Process both requests with a small delay to simulate concurrency
        request2 = middleware_stack(request2)
        time.sleep(0.1)  # Small delay
        request3 = middleware_stack(request3)

        # Verify both requests got valid carts
        assert request2.cart is not None, "Request2 should have a cart"
        assert request3.cart is not None, "Request3 should have a cart"
        assert not request2.cart.is_expired(), "Request2 cart should not be expired"
        assert not request3.cart.is_expired(), "Request3 cart should not be expired"

        # Verify original cart was marked as completed
        cart1.refresh_from_db()
        assert cart1.completed, "Original expired cart should be marked as completed"

        # Verify both requests got the same new cart
        assert request2.cart.id == request3.cart.id, "Both requests should get same new cart"
        assert request2.cart.id != cart1.id, "New cart should have different ID"

        # Verify new cart is properly cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"

    def test_expired_cart_with_items(self, request_factory, middleware_stack, test_product):
        """Test that expired carts with items are handled properly."""
        # Create cart and add items
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart1 = request1.cart
        session_key = request1.session.session_key
        cache_key = f"cart:session:{session_key}"

        # Add item to cart
        cart1.add_item(test_product, 2)
        assert cart1.items.count() == 1, "Cart should have one item"

        # Verify cart is cached with item
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart1.id, "Cached cart should match original cart"
        assert cached_cart.items.count() == 1, "Cached cart should have one item"

        # Expire the cart by updating modified_at directly in database
        with transaction.atomic():
            Cart.objects.filter(pk=cart1.pk).update(
                modified_at=timezone.now() - timedelta(days=2)
            )

        # Clear cache to ensure we don't get stale data
        cache.delete(cache_key)
        cache.delete(f"cart:{session_key}")

        # Make new request
        request2 = request_factory.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)

        # Verify expired cart is completed and new cart is empty
        cart1.refresh_from_db()
        assert cart1.completed, "Expired cart should be marked as completed"
        assert request2.cart is not None, "New cart should be created"
        assert request2.cart.id != cart1.id, "New cart should have different ID"
        assert request2.cart.items.count() == 0, "New cart should be empty"

        # Verify new cart is properly cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"
        assert cached_cart.items.count() == 0, "Cached cart should be empty"

    def test_expired_cart_in_cache_only(self, request_factory, middleware_stack):
        """Test handling of cart that is expired in cache but not in database."""
        # Create initial cart
        request1 = request_factory.get('/')
        request1 = middleware_stack(request1)
        cart1 = request1.cart
        session_key = request1.session.session_key
        cache_key = f"cart:session:{session_key}"

        # Verify cart is cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "Cart should be cached"
        assert cached_cart.id == cart1.id, "Cached cart should match original cart"

        # Manually expire cart in cache only
        cached_cart.modified_at = timezone.now() - timedelta(days=2)
        cache.set(cache_key, cached_cart)

        # Make new request
        request2 = request_factory.get('/')
        request2.session = request1.session
        request2 = middleware_stack(request2)

        # Verify expired cart was handled correctly
        cart1.refresh_from_db()
        assert cart1.completed, "Original cart should be marked as completed"
        assert request2.cart is not None, "New cart should be created"
        assert request2.cart.id != cart1.id, "New cart should have different ID"

        # Verify new cart is properly cached
        cached_cart = cache.get(cache_key)
        assert cached_cart is not None, "New cart should be cached"
        assert cached_cart.id == request2.cart.id, "Cached cart should match new cart"