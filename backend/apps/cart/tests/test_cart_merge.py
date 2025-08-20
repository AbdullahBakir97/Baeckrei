from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Cart
from apps.accounts.models import Customer
from apps.products.models import Product
from ..services.cart_retriever import CartRetriever

class CartMergeTestCase(TestCase):
    def test_merge_conflicting_items(self):
        # Setup test data
        user = User.objects.create(username='testuser')
        customer = Customer.objects.create(user=user)
        session_cart = Cart.objects.create(session_key='test_session')
        user_cart = Cart.objects.create(customer=customer)
        
        # Create conflicting items
        product = Product.objects.create(name='Test Product', stock=10, price=9.99)
        session_item = session_cart.items.create(product=product, quantity=3)
        user_item = user_cart.items.create(product=product, quantity=2)
        
        # Perform merge
        merged_cart = CartRetriever.merge_guest_cart_to_customer(customer, 'test_session')
        
        # Verify merged quantity
        merged_item = merged_cart.items.get(product=product)
        self.assertEqual(merged_item.quantity, 5)
        
        # Verify stock consistency
        product.refresh_from_db()
        self.assertEqual(product.stock, 5)
