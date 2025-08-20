import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.cart.models import Cart, CartItem
from apps.cart.exceptions import VersionConflict
from django.db import transaction


@pytest.mark.django_db
class TestCartManager:
    def test_get_or_create_active_cart_for_customer(self, test_customer):
        """Test creating and retrieving active cart for customer."""
        # Create new cart
        cart1, created1 = Cart.objects.get_or_create_active_cart(customer=test_customer)
        assert created1
        assert cart1.customer == test_customer
        
        # Try to get same cart
        cart2, created2 = Cart.objects.get_or_create_active_cart(customer=test_customer)
        assert not created2
        assert cart1 == cart2
    
    def test_get_or_create_active_cart_for_session(self):
        """Test creating and retrieving active cart for session."""
        session_key = 'test_session_123'
        
        # Create new cart
        cart1, created1 = Cart.objects.get_or_create_active_cart(session_key=session_key)
        assert created1
        assert cart1.session_key == session_key
        
        # Try to get same cart
        cart2, created2 = Cart.objects.get_or_create_active_cart(session_key=session_key)
        assert not created2
        assert cart1 == cart2
    
    def test_get_or_create_active_cart_validation(self):
        """Test validation when creating cart without customer or session."""
        with pytest.raises(ValueError):
            Cart.objects.get_or_create_active_cart()

    def test_active_carts(self, test_customer):
        """Test filtering active carts."""
        # Create active cart
        active_cart = Cart.objects.create(customer=test_customer)
        
        # Create completed cart
        completed_cart = Cart.objects.create(
            customer=test_customer,
            completed=True,
            completed_at=timezone.now()
        )
        
        # Test active filter
        active_carts = Cart.objects.active()
        assert active_cart in active_carts
        assert completed_cart not in active_carts

    def test_completed_carts(self, test_customer):
        """Test filtering completed carts."""
        # Create active cart
        active_cart = Cart.objects.create(customer=test_customer)
        
        # Create completed cart
        completed_cart = Cart.objects.create(
            customer=test_customer,
            completed=True,
            completed_at=timezone.now()
        )
        
        # Test completed filter
        completed_carts = Cart.objects.completed()
        assert completed_cart in completed_carts
        assert active_cart not in completed_carts

    def test_expired_carts(self, test_customer):
        """Test filtering expired carts."""
        # Create recent cart
        recent_cart = Cart.objects.create(
            customer=test_customer,
            session_key='recent_session'
        )
        
        # Create old cart with different customer
        from apps.accounts.models import User, Customer
        import uuid
        
        # Create user first
        old_user = User.objects.create_user(
            email='old@example.com',
            password='testpass123',
            first_name='Old',
            last_name='User'
        )
        
        # Then create customer with the user
        old_customer = Customer.objects.create(
            user=old_user,
            customer_id=str(uuid.uuid4())
        )
        
        # Create old cart and update its modified_at using update to bypass auto_now
        old_cart = Cart.objects.create(
            customer=old_customer,
            session_key='old_session'
        )
        
        # Update modified_at using update to bypass auto_now
        Cart.objects.filter(id=old_cart.id).update(
            modified_at=timezone.now() - timezone.timedelta(hours=25)
        )
        old_cart.refresh_from_db()
        
        # Test expired filter (24 hours)
        expired_carts = Cart.objects.expired()
        assert old_cart in expired_carts
        assert recent_cart not in expired_carts

    def test_for_customer(self, test_customer):
        """Test filtering carts by customer."""
        # Create cart for test customer
        customer_cart = Cart.objects.create(customer=test_customer)
        
        # Create guest cart
        guest_cart = Cart.objects.create(session_key='test_session')
        
        # Test customer filter
        customer_carts = Cart.objects.for_customer(test_customer)
        assert customer_cart in customer_carts
        assert guest_cart not in customer_carts

    def test_for_session(self):
        """Test filtering carts by session."""
        session_key = 'test_session'
        
        # Create session cart
        session_cart = Cart.objects.create(session_key=session_key)
        
        # Create customer cart
        customer_cart = Cart.objects.create(customer=None)
        
        # Test session filter
        session_carts = Cart.objects.for_session(session_key)
        assert session_cart in session_carts
        assert customer_cart not in session_carts

    def test_with_total_value(self, test_cart_with_item):
        """Test annotating carts with total value."""
        # Get cart with total value annotation
        cart = Cart.objects.with_total_value().get(id=test_cart_with_item.id)
        
        # Calculate expected total
        expected_total = sum(item.total_price for item in test_cart_with_item.items.all())
        
        # Verify annotation
        assert cart.total_value == expected_total

    def test_get_for_update_with_version(self, test_cart):
        """Test getting cart with version check."""
        # Get cart with correct version
        cart = Cart.objects.get_for_update_with_version(test_cart.id, test_cart.version)
        assert cart == test_cart
        
        # Try with wrong version
        with pytest.raises(VersionConflict):
            Cart.objects.get_for_update_with_version(test_cart.id, test_cart.version + 1)
        
        # Try with non-existent cart
        with pytest.raises(Cart.DoesNotExist):
            Cart.objects.get_for_update_with_version(9999, 1)

    def test_increment_version(self, test_cart):
        """Test incrementing cart version."""
        original_version = test_cart.version
        
        # Increment version
        new_version = Cart.objects.increment_version(test_cart.id)
        
        # Verify increment
        assert new_version == original_version + 1
        test_cart.refresh_from_db()
        assert test_cart.version == new_version


@pytest.mark.django_db
class TestCartItemManager:
    def test_active(self, test_cart_with_item):
        """Test filtering active cart items."""
        # Create completed cart with item
        completed_cart = Cart.objects.create(completed=True)
        completed_cart_item = CartItem.objects.create(
            cart=completed_cart,
            product=test_cart_with_item.items.first().product,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Test active filter
        active_items = CartItem.objects.active()
        assert test_cart_with_item.items.first() in active_items
        assert completed_cart_item not in active_items

    def test_for_product(self, test_cart_with_item, test_product):
        """Test filtering cart items by product."""
        # Get existing item
        existing_item = test_cart_with_item.items.first()
        existing_product = existing_item.product
        
        # Create new product for different item
        from apps.products.models import Product, Category
        import uuid
        category_name = f"Test Category {uuid.uuid4().hex[:8]}"
        category = Category.objects.create(
            name=category_name,
            slug=category_name.lower().replace(" ", "-")
        )
        
        different_product = Product.objects.create(
            name="Different Product",
            price=Decimal('10.00'),
            stock=10,
            category=category
        )
        
        # Create item with different product
        different_cart = Cart.objects.create()
        different_item = CartItem.objects.create(
            cart=different_cart,
            product=different_product,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Create item with null product
        null_item = CartItem.objects.create(
            cart=different_cart,
            product=None,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Test product filter
        product_items = CartItem.objects.for_product(existing_product)
        assert existing_item in product_items
        assert different_item not in product_items
        assert null_item not in product_items
        
        # Test with null product
        null_product_items = CartItem.objects.for_product(None)
        assert null_item in null_product_items
        assert existing_item not in null_product_items
        
        # Test with null product
        null_product_items = CartItem.objects.for_product(None)
        assert null_item in null_product_items
        assert existing_item not in null_product_items

    def test_active_with_null_product(self, test_cart_with_item):
        """Test filtering active cart items with null products."""
        # Create completed cart with null product item
        completed_cart = Cart.objects.create(completed=True)
        completed_null_item = CartItem.objects.create(
            cart=completed_cart,
            product=None,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Create active cart with null product item
        active_cart = Cart.objects.create()
        active_null_item = CartItem.objects.create(
            cart=active_cart,
            product=None,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Test active filter
        active_items = CartItem.objects.active()
        assert active_null_item in active_items
        assert completed_null_item not in active_items

    def test_with_subtotal(self, test_cart_with_item):
        """Test annotating cart items with subtotal."""
        # Get item with subtotal annotation
        item = CartItem.objects.with_subtotal().get(id=test_cart_with_item.items.first().id)
        
        # Calculate expected subtotal
        expected_subtotal = item.quantity * item.unit_price
        
        # Verify annotation
        assert item.subtotal == expected_subtotal

    def test_out_of_stock(self, test_cart_with_item):
        """Test filtering out of stock items."""
        # Get existing item
        item = test_cart_with_item.items.first()
        
        # Set quantity higher than stock
        item.quantity = item.product.stock + 1
        item.save()
        
        # Test out of stock filter
        out_of_stock_items = CartItem.objects.out_of_stock()
        assert item in out_of_stock_items

    def test_needs_price_update(self, test_cart_with_item):
        """Test filtering items needing price update."""
        # Get existing item
        item = test_cart_with_item.items.first()
        
        # Update product price
        item.product.price = item.unit_price + Decimal('10.00')
        item.product.save()
        
        # Test needs price update filter
        needs_update_items = CartItem.objects.needs_price_update()
        assert item in needs_update_items

    def test_bulk_update_prices(self, test_cart_with_item, test_product):
        """Test bulk updating cart item prices."""
        # Get the item and note its current version
        item = test_cart_with_item.items.first()
        original_price = item.unit_price
        original_version = item.version
        
        # Update product price
        test_product.price = Decimal('25.99')
        test_product.save()
        
        # Verify item needs update
        item.refresh_from_db()
        assert item.unit_price == original_price
        assert item.version == original_version
        
        # Perform bulk update with version handling
        with transaction.atomic():
            updated_count = CartItem.objects.bulk_update_prices()
            assert updated_count == 1
            
            # Verify price and version were updated
            item.refresh_from_db()
            assert item.unit_price == Decimal('25.99')
            assert item.version == original_version + 1

    def test_bulk_update_prices_with_null_product(self, test_cart_with_item):
        """Test bulk updating cart item prices with null products."""
        # Create item with null product
        cart = Cart.objects.create()
        null_item = CartItem.objects.create(
            cart=cart,
            product=None,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        
        # Perform bulk update
        with transaction.atomic():
            updated_count = CartItem.objects.bulk_update_prices()
            # Null product items should be skipped
            assert updated_count == 0
            
            # Verify price was not updated
            null_item.refresh_from_db()
            assert null_item.unit_price == Decimal('10.00')

    def test_get_for_update_with_version(self, test_cart_with_item):
        """Test getting cart item with version check."""
        item = test_cart_with_item.items.first()
        
        # Get item with correct version
        locked_item = CartItem.objects.get_for_update_with_version(item.id, item.version)
        assert locked_item == item
        
        # Try with wrong version
        with pytest.raises(VersionConflict):
            CartItem.objects.get_for_update_with_version(item.id, item.version + 1)
        
        # Try with non-existent item
        with pytest.raises(CartItem.DoesNotExist):
            CartItem.objects.get_for_update_with_version(9999, 1)

    def test_increment_version(self, test_cart_with_item):
        """Test incrementing cart item version."""
        item = test_cart_with_item.items.first()
        original_version = item.version
        
        # Increment version
        new_version = CartItem.objects.increment_version(item.id)
        
        # Verify increment
        assert new_version == original_version + 1
        item.refresh_from_db()
        assert item.version == new_version

    def test_get_with_stock_check(self, test_cart_with_item):
        """Test getting cart item with stock check."""
        item = test_cart_with_item.items.first()
        
        # Get item with stock check
        checked_item = CartItem.objects.get_with_stock_check(item.id)
        
        # Verify product is selected
        assert checked_item.product == item.product
        assert checked_item == item

    def test_get_with_stock_check_scenarios(self, test_cart_with_item):
        """Test getting cart item with stock check in various scenarios."""
        item = test_cart_with_item.items.first()
        
        # Test with in-stock item
        checked_item = CartItem.objects.get_with_stock_check(item.id)
        assert checked_item.product == item.product
        assert checked_item == item
        
        # Test with out-of-stock item
        item.quantity = item.product.stock + 1
        item.save()
        checked_item = CartItem.objects.get_with_stock_check(item.id)
        assert checked_item.quantity > checked_item.product.stock
        
        # Test with null product
        null_item = CartItem.objects.create(
            cart=test_cart_with_item,
            product=None,
            quantity=1,
            unit_price=Decimal('10.00')
        )
        checked_null_item = CartItem.objects.get_with_stock_check(null_item.id)
        assert checked_null_item.product is None
        assert checked_null_item == null_item
