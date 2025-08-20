import pytest
from decimal import Decimal
from django.test import TestCase, Client
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.cart.models import Cart, CartItem
from apps.products.models import Product, Category
from apps.accounts.models import Customer

pytestmark = pytest.mark.django_db

class TestCartWorkflows(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='1234567890'
        )
        self.customer = Customer.objects.create(
            user=self.user
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Create test products with category
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=Decimal('10.00'),
            stock=10,
            category=self.category,
            available=True,
            status='active'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=Decimal('20.00'),
            stock=5,
            category=self.category,
            available=True,
            status='active'
        )

    def test_guest_shopping_workflow(self):
        """Test complete shopping workflow for guest user."""
        # 1. Browse products - skip this step since we don't have products:list URL
        # response = self.client.get(reverse('products:list'))
        # assert response.status_code == 200
        
        # 2. Add first product to cart
        response = self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        assert response.status_code == 200
        
        # 3. View cart
        response = self.client.get(reverse('cart:cart-detail'))
        assert response.status_code == 200
        assert len(response.data['data']['items']) == 1
        
        # 4. Add second product
        response = self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        assert response.status_code == 200
        
        # 5. Update quantity of first product
        response = self.client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': str(self.product1.id)}),
            data=json.dumps({'quantity': 3}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 6. Remove second product
        response = self.client.delete(
            reverse('cart:remove-from-cart', kwargs={'product_id': str(self.product2.id)})
        )
        assert response.status_code == 200
        
        # 7. Verify final cart state
        response = self.client.get(reverse('cart:cart-detail'))
        assert len(response.data['data']['items']) == 1
        assert response.data['data']['total'] == '35.70'  # 3 * 10.00 * 1.19

    def test_user_registration_workflow(self):
        """Test workflow where guest user registers during checkout."""
        # 1. Add items as guest
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        
        # Get guest cart data and session key
        guest_response = self.client.get(reverse('cart:cart-detail'))
        guest_cart_id = guest_response.data['data']['id']
        guest_session_key = self.client.session.session_key
        
        # Store session key before login
        session = self.client.session
        session['_auth_user_pre_login_session_key'] = guest_session_key
        session.save()
        
        # Get the guest cart to verify it exists
        guest_cart = Cart.objects.get(id=guest_cart_id)
        self.assertEqual(guest_cart.session_key, guest_session_key)
        
        # 2. Login directly instead of registration
        self.client.login(email='test@example.com', password='testpass123')
        
        # Force session save to ensure changes are persisted
        self.client.session.save()
        
        # 3. Verify cart was transferred
        response = self.client.get(reverse('cart:cart-detail'))
        assert len(response.data['data']['items']) > 0
        assert response.data['data']['id'] != guest_cart_id

    def test_cart_expiry_workflow(self):
        """Test cart behavior with session expiry."""
        # 1. Add items to cart
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product1.id),
            'quantity': 1
        })
        
        # 2. Get current session key
        original_session = self.client.session.session_key
        
        # 3. Simulate session expiry by creating new session
        self.client.session.flush()
        
        # 4. Verify new cart is created
        response = self.client.get(reverse('cart:cart-detail'))
        assert response.data['data']['items'] == []
        assert self.client.session.session_key != original_session

    def test_cart_merge_workflow(self):
        """Test cart merging when user logs in with existing cart."""
        # 1. Create items in guest cart
        guest_response = self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        guest_cart_id = guest_response.data['data']['id']

        # Store guest session key
        guest_session_key = self.client.session.session_key

        # Verify guest cart exists and has items
        guest_cart = Cart.objects.get(id=guest_cart_id)
        self.assertEqual(guest_cart.session_key, guest_session_key)
        self.assertEqual(guest_cart.items.count(), 1)
        self.assertEqual(guest_cart.items.first().quantity, 2)

        # 2. Create authenticated cart
        auth_client = Client()
        auth_client.force_login(self.user)
        auth_response = auth_client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        auth_cart_id = auth_response.data['data']['id']

        # Verify authenticated cart exists and has items
        auth_cart = Cart.objects.get(id=auth_cart_id)
        self.assertEqual(auth_cart.customer, self.customer)
        self.assertEqual(auth_cart.items.count(), 1)
        self.assertEqual(auth_cart.items.first().quantity, 1)

        # 3. Login guest user and preserve session
        # First store the session key
        session = self.client.session
        session['_auth_user_pre_login_session_key'] = guest_session_key
        session.save()

        # Then force login
        self.client.force_login(self.user)

        # 4. Verify carts are merged
        response = self.client.get(reverse('cart:cart-detail'))
        self.assertEqual(response.status_code, 200)
        
        # Get the merged cart
        merged_cart = Cart.objects.get(customer=self.customer, completed=False)
        self.assertEqual(merged_cart.items.count(), 2, "Cart should have both items after merge")
        
        # Verify each item is present with correct quantity
        items = merged_cart.items.all()
        item_quantities = {str(item.product.id): item.quantity for item in items}
        self.assertEqual(item_quantities.get(str(self.product1.id)), 2, "First product quantity should be 2")
        self.assertEqual(item_quantities.get(str(self.product2.id)), 1, "Second product quantity should be 1")

    def test_stock_validation_workflow(self):
        """Test cart behavior with stock limitations."""
        # 1. Add maximum available stock
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product2.id),
            'quantity': 5  # Max stock
        })
        
        # 2. Try to add more than available
        response = self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        assert response.status_code == 400
        assert 'stock' in str(response.data['detail']).lower()
        
        # 3. Update quantity beyond stock
        response = self.client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': str(self.product2.id)}),
            {'quantity': 6}
        )
        assert response.status_code == 400
        
        # 4. Verify cart quantity unchanged
        response = self.client.get(reverse('cart:cart-detail'))
        assert response.data['data']['items'][0]['quantity'] == 5

    def test_cart_calculation_workflow(self):
        """Test cart calculations through various operations."""
        # 1. Add first item
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        response = self.client.get(reverse('cart:cart-detail'))
        subtotal1 = Decimal(response.data['data']['subtotal'])
        assert subtotal1 == Decimal('20.00')
        
        # 2. Add second item
        self.client.post(reverse('cart:add-to-cart'), {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        response = self.client.get(reverse('cart:cart-detail'))
        subtotal2 = Decimal(response.data['data']['subtotal'])
        assert subtotal2 == Decimal('40.00')
        
        # 3. Update quantity with proper content type
        response = self.client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': str(self.product1.id)}),
            data=json.dumps({'quantity': 1}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 4. Verify tax and total
        response = self.client.get(reverse('cart:cart-detail'))
        subtotal3 = Decimal(response.data['data']['subtotal'])
        assert subtotal3 == Decimal('30.00')
        assert Decimal(response.data['data']['tax']) == subtotal3 * Decimal('0.19')  # 19% VAT
        assert Decimal(response.data['data']['total']) == subtotal3 * Decimal('1.19')