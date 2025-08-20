"""Base test case for cart tests."""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.accounts.models import Customer, User
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from apps.cart.services.cart_retriever import CartRetriever

class CartTestCase(TestCase):
    """Base test case with common setup for cart tests."""

    def setUp(self):
        """Set up test data."""
        # Create test user and customer
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.test_customer = Customer.objects.create(
            user=self.user
        )

        # Create test category
        self.test_category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category for cart tests'
        )

        # Create test products
        self.test_product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            stock=100,
            available=True,
            status='active',
            category=self.test_category
        )
        
        self.test_product_2 = Product.objects.create(
            name='Test Product 2',
            price=Decimal('20.00'),
            stock=50,
            available=True,
            status='active',
            category=self.test_category
        )

        # Create cart retriever
        self.cart_retriever = CartRetriever()

    def create_test_cart(self, customer=None, session_key=None):
        """Create a test cart."""
        return Cart.objects.create(
            customer=customer,
            session_key=session_key,
            version=1
        )

    def add_item_to_cart(self, cart, product, quantity=1):
        """Add an item to cart."""
        return cart.add_item(product, quantity)

    def create_cart_with_items(self, customer=None, session_key=None, items=None):
        """Create a cart with specified items.
        
        Args:
            customer: Optional customer to associate with cart
            session_key: Optional session key for guest cart
            items: List of tuples (product, quantity) to add to cart
        """
        cart = self.create_test_cart(customer, session_key)
        if items:
            for product, quantity in items:
                self.add_item_to_cart(cart, product, quantity)
        return cart

    def assert_cart_item_count(self, cart, expected_count):
        """Assert cart has expected number of items."""
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), expected_count)

    def assert_cart_totals(self, cart, expected_total_items, expected_subtotal):
        """Assert cart totals are correct."""
        cart.refresh_from_db()
        self.assertEqual(cart.total_items, expected_total_items)
        self.assertEqual(cart.subtotal, Decimal(str(expected_subtotal)))

    def assert_product_stock(self, product, expected_stock):
        """Assert product stock is correct."""
        product.refresh_from_db()
        self.assertEqual(product.stock, expected_stock)

    def simulate_concurrent_update(self, cart):
        """Simulate a concurrent update to cart."""
        # Create a separate instance of the same cart
        concurrent_cart = Cart.objects.get(pk=cart.pk)
        concurrent_cart.version += 1
        concurrent_cart.save()
