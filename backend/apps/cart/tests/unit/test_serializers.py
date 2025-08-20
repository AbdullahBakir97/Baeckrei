import pytest
from decimal import Decimal
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from apps.cart.serializers import (
    CartSerializer,
    CartItemSerializer,
    CartOperationSerializer,
    CartDetailSerializer,
    AddToCartSerializer
)
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from django.utils import timezone
import uuid

class TestCartSerializers(TestCase):
    def setUp(self):
        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test Category Description'
        )
        
        # Create product
        self.product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': Decimal('10.00'),
            'stock': 10,
            'available': True,
            'status': 'active',
            'category': self.category
        }
        self.product = Product.objects.create(**self.product_data)
        
        # Create cart and cart item
        self.cart = Cart.objects.create()
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )

    def test_cart_item_serializer(self):
        """Test CartItemSerializer functionality."""
        # Test serialization
        serializer = CartItemSerializer(instance=self.cart_item)
        data = serializer.data
        
        self.assertEqual(data['quantity'], 2)
        self.assertEqual(Decimal(data['unit_price']), self.product.price)
        self.assertEqual(data['product_name'], self.product.name)
        self.assertEqual(Decimal(data['product_price']), self.product.price)
        self.assertEqual(data['available_stock'], self.product.stock)
        
        # Test validation
        invalid_data = {
            'quantity': 0,
            'product': self.product.id
        }
        serializer = CartItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)

    def test_cart_serializer(self):
        """Test CartSerializer functionality."""
        serializer = CartSerializer(instance=self.cart)
        data = serializer.data
        
        # Test basic fields
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertIn('subtotal', data)
        self.assertIn('tax', data)
        self.assertIn('total_items', data)
        
        # Test computed values
        self.assertEqual(Decimal(data['subtotal']), self.cart_item.quantity * self.cart_item.unit_price)
        self.assertEqual(int(data['total_items']), self.cart_item.quantity)  # Should be sum of quantities
        
    def test_cart_detail_serializer(self):
        """Test CartDetailSerializer functionality."""
        # Create another product
        different_product = Product.objects.create(
            name='Different Product',
            description='Another Test Description',
            price=Decimal('15.00'),
            stock=5,
            available=True,
            status='active',
            category=self.category
        )
        
        # Create another cart item with different product
        CartItem.objects.create(
            cart=self.cart,
            product=different_product,
            quantity=1,
            unit_price=different_product.price
        )
        
        serializer = CartDetailSerializer(instance=self.cart)
        data = serializer.data
        
        # Test additional computed fields
        self.assertEqual(data['items_count'], 3)  # Total items (first item qty=2 + second item qty=1)
        self.assertEqual(data['unique_items'], 2)  # Number of unique items
        self.assertFalse(data['has_out_of_stock'])  # Stock check
        
        # Verify individual quantities
        items = data['items']
        self.assertEqual(len(items), 2)  # Two unique items
        quantities = [item['quantity'] for item in items]
        self.assertCountEqual(quantities, [2, 1])  # One item with qty=2, one with qty=1
        
        # Test out of stock detection
        different_product.stock = 0
        different_product.save()
        
        serializer = CartDetailSerializer(instance=self.cart)
        data = serializer.data
        self.assertTrue(data['has_out_of_stock'])

    def test_cart_operation_serializer(self):
        """Test CartOperationSerializer validation."""
        # Test valid data
        valid_data = {
            'product_id': str(self.product.id),
            'quantity': 1
        }
        serializer = CartOperationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid UUID
        invalid_data = {
            'product_id': 'not-a-uuid',
            'quantity': 1
        }
        serializer = CartOperationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_id', serializer.errors)
        
        # Test non-existent product
        invalid_data = {
            'product_id': str(uuid.uuid4()),
            'quantity': 1
        }
        serializer = CartOperationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # Test negative quantity
        invalid_data = {
            'product_id': str(self.product.id),
            'quantity': -1
        }
        serializer = CartOperationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # Test quantity exceeding stock
        invalid_data = {
            'product_id': str(self.product.id),
            'quantity': self.product.stock + 1
        }
        serializer = CartOperationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_add_to_cart_serializer_validation(self):
        """Test AddToCartSerializer validation."""
        # Test valid data
        valid_data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        serializer = AddToCartSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Test invalid quantity
        invalid_data = {
            'product_id': self.product.id,
            'quantity': 0
        }
        serializer = AddToCartSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)

        # Test non-existent product
        invalid_data = {
            'product_id': uuid.uuid4(),
            'quantity': 1
        }
        serializer = AddToCartSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_id', serializer.errors)

        # Test quantity exceeding stock
        invalid_data = {
            'product_id': self.product.id,
            'quantity': self.product.stock + 1
        }
        serializer = AddToCartSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)
        
        # Test inactive product
        self.product.status = 'inactive'
        self.product.save()
        
        invalid_data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        serializer = AddToCartSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_id', serializer.errors)