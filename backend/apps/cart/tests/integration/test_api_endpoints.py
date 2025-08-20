import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, force_authenticate
from apps.cart.models import Cart, CartItem
from apps.cart.services.cart_retriever import CartRetriever
from apps.products.models import Product
from django.contrib.auth import get_user_model
from django.test import RequestFactory, modify_settings
from django.core.cache import cache
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY

pytestmark = pytest.mark.django_db

class TestCartAPIEndpoints:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client, test_user, test_customer, test_cart):
        """Create an authenticated API client with proper user and customer setup."""
        client = APIClient()
        
        # Create a session
        session = SessionStore()
        session.create()
        
        # Set up session auth
        session[SESSION_KEY] = str(test_user.id)
        session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
        session[HASH_SESSION_KEY] = test_user.get_session_auth_hash()
        session.save()
        
        # Set session cookie
        client.cookies['sessionid'] = session.session_key
        
        # Set up client
        client.force_authenticate(user=test_user)
        
        # Set user and customer attributes
        client._cached_user = test_user
        client.customer = test_customer
        client.cart = test_cart
        
        # Cache the customer and cart
        cache.set(f"customer:user:{test_user.id}", test_customer)
        cache.set(f"cart:user:{test_user.id}", test_cart)
        cache.set(f"cart:session:{session.session_key}", test_cart)
        
        return client

    @pytest.fixture
    def test_cart(self, test_customer):
        """Create a test cart for the authenticated customer."""
        cart = Cart.objects.create(customer=test_customer)
        return cart

    def test_get_cart_authenticated(self, authenticated_client, test_cart):
        """Test retrieving cart for authenticated user."""
        url = reverse('cart:cart-detail')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert response.data['data']['id'] == test_cart.id
        assert Decimal(response.data['data']['total']) == test_cart.total

    def test_get_cart_anonymous(self, api_client):
        """Test retrieving cart for anonymous user."""
        url = reverse('cart:cart-detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'session_key' in response.data['data']

    def test_add_to_cart(self, authenticated_client, test_cart, test_product):
        """Test adding item to cart."""
        url = reverse('cart:add-to-cart')
        data = {
            'product_id': str(test_product.id),
            'quantity': 2
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert CartItem.objects.filter(cart=test_cart, product=test_product).exists()
        
        cart_item = CartItem.objects.get(cart=test_cart, product=test_product)
        assert cart_item.quantity == 2
        assert cart_item.unit_price == test_product.price

    def test_add_to_cart_invalid_quantity(self, authenticated_client, test_product):
        """Test adding item with invalid quantity."""
        url = reverse('cart:add-to-cart')
        data = {
            'product_id': str(test_product.id),
            'quantity': 0
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'quantity' in str(response.data['detail']).lower()

    def test_update_cart_item(self, authenticated_client, test_cart_with_item):
        """Test updating cart item quantity."""
        cart_item = test_cart_with_item.items.first()
        url = reverse('cart:update-cart-item', kwargs={'product_id': str(cart_item.product.id)})
        data = {'quantity': 3}
        
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_remove_from_cart(self, authenticated_client, test_cart_with_item):
        """Test removing item from cart."""
        cart_item = test_cart_with_item.items.first()
        url = reverse('cart:remove-from-cart', kwargs={'product_id': str(cart_item.product.id)})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(id=cart_item.id).exists()

    def test_clear_cart(self, authenticated_client, test_cart_with_item):
        """Test clearing all items from cart."""
        url = reverse('cart:clear-cart')
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert test_cart_with_item.items.count() == 0

    def test_merge_carts_on_login(self, api_client, test_user, test_customer, test_product):
        """Test merging guest cart with customer cart on login."""
        # First create a guest cart and add an item
        guest_response = api_client.get(reverse('cart:cart-detail'))
        guest_cart_id = guest_response.data['data']['id']
        
        # Add item to guest cart
        api_client.post(reverse('cart:add-to-cart'), {
            'product_id': str(test_product.id),
            'quantity': 2
        })
        
        # Store session key before login
        session_key = api_client.session.session_key
        
        # Get the guest cart before login
        guest_cart = Cart.objects.get(session_key=session_key)
        assert guest_cart.items.count() == 1
        
        # Now login and set up customer
        api_client.force_authenticate(user=test_user)
        api_client._cached_user = test_user
        
        # Create a new cart for the customer
        customer_cart = Cart.objects.create(customer=test_customer)
        
        # Manually trigger cart merge since we're in a test
        CartRetriever.merge_guest_cart_to_customer(test_customer, session_key)
        
        # Get cart after login - this should now show the merged cart
        response = api_client.get(reverse('cart:cart-detail'))
        
        # Verify response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the guest cart was merged into customer cart
        customer_cart.refresh_from_db()
        assert customer_cart.items.count() == 1
        cart_item = customer_cart.items.first()
        assert cart_item.product == test_product
        assert cart_item.quantity == 2
        
        # Verify the guest cart is marked as completed
        guest_cart.refresh_from_db()
        assert guest_cart.completed

    def test_cart_item_stock_validation(self, authenticated_client, test_cart, test_product):
        """Test stock validation when adding items."""
        url = reverse('cart:add-to-cart')
        data = {
            'product_id': str(test_product.id),
            'quantity': test_product.stock + 1
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'stock' in str(response.data['detail']).lower()

    def test_cart_session_fixation_prevention(self, api_client):
        """Test session fixation prevention for anonymous users."""
        # Try to use a fixed session key
        api_client.cookies['sessionid'] = 'fixed-session-key'
        
        url = reverse('cart:cart-detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        session_key = api_client.session.session_key
        assert session_key != 'fixed-session-key'