import pytest
import threading
import time
from decimal import Decimal
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.accounts.models import Customer
from django.db.utils import OperationalError
import concurrent.futures

pytestmark = pytest.mark.django_db

class TestCartConcurrency(TransactionTestCase):
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
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            stock=10
        )

    def test_concurrent_cart_creation(self):
        """Test concurrent cart creation for the same user."""
        def create_cart():
            client = Client()
            client.force_login(self.user)
            return client.get(reverse('cart:cart-detail'))
        
        # Create multiple carts concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_cart) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        # Verify only one cart was created
        carts = Cart.objects.filter(customer=self.customer, completed=False)
        assert len(carts) == 1

    def test_concurrent_add_to_cart(self):
        """Test concurrent add-to-cart operations."""
        def add_to_cart(quantity):
            client = Client()
            client.force_login(self.user)
            return client.post(reverse('cart:add-to-cart'), {
                'product_id': str(self.product.id),
                'quantity': quantity
            })
        
        # Add items concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(add_to_cart, 1) for _ in range(5)]
            responses = [f.result() for f in futures]
        
        # Verify total quantity doesn't exceed stock
        cart = Cart.objects.get(customer=self.customer)
        assert cart.items.first().quantity <= self.product.stock

    def test_concurrent_cart_updates(self):
        """Test concurrent cart item updates."""
        # Create initial cart item
        self.client.force_login(self.user)
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product.id),
            'quantity': 1
        })
        
        def update_cart(quantity):
            client = Client()
            client.force_login(self.user)
            return client.put(
                reverse('cart:update-cart-item', kwargs={'product_id': str(self.product.id)}),
                {'quantity': quantity}
            )
        
        # Update quantity concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_cart, i) for i in range(1, 6)]
            responses = [f.result() for f in futures]
        
        # Verify final quantity is valid
        cart = Cart.objects.get(customer=self.customer)
        assert cart.items.first().quantity <= self.product.stock

    def test_concurrent_stock_updates(self):
        """Test concurrent stock updates with cart operations."""
        self.client.force_login(self.user)
        
        def update_stock():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=self.product.id)
                product.stock -= 1
                product.save()
        
        def add_to_cart():
            client = Client()
            client.force_login(self.user)
            return client.post(reverse('cart:add-to-cart'), {
                'product_id': str(self.product.id),
                'quantity': 1
            })
        
        # Run stock updates and cart additions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            stock_futures = [executor.submit(update_stock) for _ in range(5)]
            cart_futures = [executor.submit(add_to_cart) for _ in range(5)]
            
            # Wait for all operations to complete
            concurrent.futures.wait(stock_futures + cart_futures)
        
        # Verify stock consistency
        self.product.refresh_from_db()
        cart = Cart.objects.get(customer=self.customer)
        total_quantity = sum(item.quantity for item in cart.items.all())
        assert total_quantity + self.product.stock <= 10  # Original stock

    def test_concurrent_cart_merges(self):
        """Test concurrent cart merges during login."""
        def create_guest_cart():
            client = Client()
            client.post(reverse('cart:add-to-cart'), {
                'product_id': str(self.product.id),
                'quantity': 1
            })
            return client
        
        # Create multiple guest carts
        guest_clients = [create_guest_cart() for _ in range(5)]
        
        def merge_cart(client):
            client.force_login(self.user)
            return client.get(reverse('cart:cart-detail'))
        
        # Merge carts concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(merge_cart, client) for client in guest_clients]
            responses = [f.result() for f in futures]
        
        # Verify final cart state
        cart = Cart.objects.get(customer=self.customer, completed=False)
        assert cart.items.count() == 1
        assert cart.items.first().quantity <= self.product.stock

    def test_concurrent_cart_clear(self):
        """Test concurrent cart clearing operations."""
        self.client.force_login(self.user)
        
        # Add items to cart
        for _ in range(5):
            self.client.post(reverse('cart:add-to-cart'), {
                'product_id': str(self.product.id),
                'quantity': 1
            })
        
        def clear_cart():
            client = Client()
            client.force_login(self.user)
            return client.post(reverse('cart:clear-cart'))
        
        # Clear cart concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_cart) for _ in range(5)]
            responses = [f.result() for f in futures]
        
        # Verify cart is empty
        cart = Cart.objects.get(customer=self.customer)
        assert cart.items.count() == 0

    def test_concurrent_session_operations(self):
        """Test concurrent operations with session handling."""
        def session_operations():
            client = Client()
            # Create cart
            response1 = client.get(reverse('cart:cart-detail'))
            session_key1 = client.session.session_key
            
            # Add item
            client.post(reverse('cart:add-to-cart'), {
                'product_id': str(self.product.id),
                'quantity': 1
            })
            
            # Simulate session change
            client.session.cycle_key()
            
            # Get cart again
            response2 = client.get(reverse('cart:cart-detail'))
            session_key2 = client.session.session_key
            
            return session_key1, session_key2, response1, response2
        
        # Run concurrent session operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(session_operations) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # Verify session handling
        for session_key1, session_key2, response1, response2 in results:
            assert session_key1 != session_key2
            assert response1.status_code == 200
            assert response2.status_code == 200

    def test_deadlock_prevention(self):
        """Test prevention of deadlocks in cart operations."""
        self.client.force_login(self.user)
        
        def update_cart_and_product():
            try:
                with transaction.atomic():
                    # Lock the product
                    product = Product.objects.select_for_update().get(id=self.product.id)
                    time.sleep(0.1)  # Simulate work
                    
                    # Lock the cart
                    cart = Cart.objects.select_for_update().get(customer=self.customer)
                    time.sleep(0.1)  # Simulate work
                    
                    # Update both
                    product.stock -= 1
                    product.save()
                    
                    if cart.items.exists():
                        item = cart.items.first()
                        item.quantity += 1
                        item.save()
                    else:
                        CartItem.objects.create(cart=cart, product=product, quantity=1)
                    
                return True
            except OperationalError:
                return False
        
        # Run concurrent updates
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_cart_and_product) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # Verify no deadlocks occurred
        assert any(results)  # At least one operation should succeed