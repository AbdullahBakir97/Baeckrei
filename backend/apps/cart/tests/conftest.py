import os
import django
from rest_framework.test import APIClient
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client
from django.core.cache import cache

# Configure Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import Customer, User
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from apps.cart.services.services import CartService

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()

@pytest.fixture
def test_user():
    """Create a test user."""
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user

@pytest.fixture
def test_customer(test_user):
    """Create a test customer."""
    customer = Customer.objects.create(
        user=test_user,
        customer_id=f'test_{test_user.id}'
    )
    return customer

@pytest.fixture
def test_category():
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        description='Test Category Description'
    )

@pytest.fixture
def test_product(test_category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        description='Test Product Description',
        category=test_category,
        price=Decimal('10.00'),
        stock=10,
        available=True,
        status='active'
    )

@pytest.fixture
def test_cart(test_customer):
    """Create a test cart."""
    cart = Cart.objects.create(
        customer=test_customer,
        version=1,
        completed=False
    )
    return cart

@pytest.fixture
def test_completed_cart(test_customer):
    """Create a completed test cart."""
    cart = Cart.objects.create(
        customer=test_customer,
        completed=True,
        completed_at=timezone.now()
    )
    return cart

@pytest.fixture
def active_product(test_category):
    """Create an active test product."""
    product = Product.objects.create(
        name='Active Product',
        description='Test Product Description',
        category=test_category,
        price=Decimal('19.99'),
        stock=10,
        available=True,
        status='active'
    )
    return product

@pytest.fixture
def authenticated_client(test_user, test_customer, test_cart):
    """Create an authenticated API client."""
    # Create and set up Django test client for session handling
    django_client = Client()
    django_client.force_login(test_user)
    django_client.session['customer_id'] = test_customer.id
    django_client.session['cart_id'] = test_cart.id
    django_client.session.save()
    
    # Create and set up DRF API client
    client = APIClient()
    client.force_authenticate(user=test_user)
    client.cookies['sessionid'] = django_client.session.session_key
    
    # Cache the customer and cart
    cache.set(f"customer:user:{test_user.id}", test_customer)
    cache.set(f"cart:user:{test_user.id}", test_cart)
    
    return client

@pytest.fixture
def empty_cart():
    """Create an empty cart."""
    return Cart.objects.create()

@pytest.fixture
def test_cart_with_item(test_cart, test_product):
    """Create a test cart with two items."""
    # Create first item
    CartItem.objects.create(
        cart=test_cart,
        product=test_product,
        quantity=2,  # Set quantity to 2 to match test expectations
        unit_price=test_product.price
    )
    return test_cart

@pytest.fixture
def test_guest_cart():
    """Create a test cart for a guest user."""
    return Cart.objects.create(session_key='test_session_key')

@pytest.fixture
def guest_cart():
    """Create a test cart for a guest."""
    return Cart.objects.create(
        session_key='test-session-key'
    )

@pytest.fixture
def test_customer_cart(test_customer, test_product):
    """Create a cart for test customer."""
    cart = Cart.objects.create(customer=test_customer)
    cart.add_item(test_product, 2)
    return cart