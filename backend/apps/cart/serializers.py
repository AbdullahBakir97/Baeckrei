from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer, ProductListSerializer
from apps.accounts.serializers import CustomerSerializer
from .exceptions import VersionConflict
import uuid
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with enhanced validation and version control."""
    product = ProductListSerializer(read_only=True)  # Nested product object
    
    def to_representation(self, instance):
        """Add debug logging to see what's being serialized."""
        logger.info(f"Serializing CartItem {instance.id}")
        logger.info(f"Product field: {instance.product}")
        logger.info(f"Product type: {type(instance.product)}")
        if instance.product:
            logger.info(f"Product ID: {instance.product.id}")
            logger.info(f"Product name: {instance.product.name}")
        
        representation = super().to_representation(instance)
        logger.info(f"Serialized representation: {representation}")
        return representation
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    version = serializers.IntegerField(read_only=True)
    available_stock = serializers.IntegerField(source='product.stock', read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_name', 'product_price',
            'quantity', 'unit_price', 'total_price', 'version',
            'available_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cart', 'unit_price', 'total_price', 'version',
            'created_at', 'updated_at'
        ]

    def validate_quantity(self, value):
        """Validate quantity against product stock and business rules."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")

        # Get current instance if we're updating
        instance = self.instance
        product = self.context.get('product') or (instance.product if instance else None)

        if not product:
            raise serializers.ValidationError("Product information is required")

        # Calculate the actual quantity change
        current_quantity = instance.quantity if instance else 0
        quantity_change = value - current_quantity

        # Check if we have enough stock
        if quantity_change > 0 and quantity_change > product.stock:
            raise serializers.ValidationError(
                f"Not enough stock. Requested change: {quantity_change}, Available: {product.stock}"
            )

        return value

    def validate_product(self, product):
        """Validate product availability and status."""
        if not product.available or product.status != 'active':
            raise serializers.ValidationError(
                f"Product {product.name} is not available for purchase"
            )
        
        # Store product in context for quantity validation
        self.context['product'] = product
        return product

    def validate(self, data):
        """Perform object-level validation."""
        if self.instance:
            try:
                # Verify version hasn't changed since last read
                current_version = CartItem.objects.filter(
                    id=self.instance.id
                ).values_list('version', flat=True).first()

                if current_version != self.instance.version:
                    raise VersionConflict("Cart item has been modified since last read")
            except CartItem.DoesNotExist:
                raise serializers.ValidationError("Cart item no longer exists")

        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create a new cart item with proper locking."""
        cart = self.context.get('cart')
        if not cart:
            raise serializers.ValidationError("Cart is required")

        try:
            # Lock the cart and check version
            cart = Cart.objects.select_for_update().get(id=cart.id)
            if cart.version != self.context.get('cart_version'):
                raise VersionConflict("Cart has been modified since last read")

            # Create cart item
            cart_item = super().create(validated_data)
            
            # Update cart version
            cart.version += 1
            cart.save()

            return cart_item
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart no longer exists")

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update cart item with version control."""
        try:
            # Lock both cart and cart item
            cart = Cart.objects.select_for_update().get(id=instance.cart.id)
            cart_item = CartItem.objects.select_for_update().get(id=instance.id)

            # Verify versions haven't changed
            if cart.version != self.context.get('cart_version'):
                raise VersionConflict("Cart has been modified since last read")
            if cart_item.version != instance.version:
                raise VersionConflict("Cart item has been modified since last read")

            # Update cart item
            updated_item = super().update(cart_item, validated_data)
            
            # Update cart version
            cart.version += 1
            cart.save()

            return updated_item
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            raise serializers.ValidationError("Cart or cart item no longer exists")

class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart data with nested items."""
    items = CartItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True)
    customer_email = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'customer_email', 'session_key', 'items', 
            'total_items', 'subtotal', 'tax', 'total', 'completed', 
            'completed_at', 'updated_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'customer', 'session_key', 'total_items', 'subtotal', 
            'tax', 'total', 'completed_at', 'created_at', 'updated_at'
        ]

    def get_customer_email(self, obj):
        """Get customer email if available."""
        if isinstance(obj, dict):
            customer = obj.get('customer')
            return customer.get('email') if customer else None
        elif hasattr(obj, 'customer') and obj.customer:
            return obj.customer.email
        return None

    def to_representation(self, instance):
        """Add computed fields to the cart representation."""
        if isinstance(instance, dict):
            # Skip response data structure
            if 'status' in instance and 'data' in instance:
                return super().to_representation(instance['data'])
            # Handle cart data dict
            cart_data = {k: v for k, v in instance.items() if k not in ['status', 'data']}
            instance = Cart(**cart_data)
        
        data = super().to_representation(instance)
        
        # Calculate total items (sum of quantities)
        items = instance.items.all() if hasattr(instance, 'items') else []
        data['total_items'] = sum(item.quantity for item in items)
        data['subtotal'] = str(instance.subtotal if hasattr(instance, 'subtotal') else Decimal('0.00'))
        data['tax'] = str(instance.tax if hasattr(instance, 'tax') else Decimal('0.00'))
        data['total'] = str(instance.total if hasattr(instance, 'total') else Decimal('0.00'))
        return data

class CartDetailSerializer(CartSerializer):
    """Detailed cart serializer with additional information."""
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='total_items', read_only=True)
    unique_items = serializers.SerializerMethodField()
    has_out_of_stock = serializers.SerializerMethodField()
    
    class Meta(CartSerializer.Meta):
        fields = CartSerializer.Meta.fields + [
            'items',
            'items_count',
            'unique_items',
            'has_out_of_stock',
        ]
    
    def get_unique_items(self, instance):
        """Get count of unique items in cart."""
        items = instance.items.all() if hasattr(instance, 'items') else []
        return len(items)
    
    def get_has_out_of_stock(self, instance):
        """Check if any items are out of stock."""
        items = instance.items.all() if hasattr(instance, 'items') else []
        return any(item.quantity > item.product.stock for item in items)

class CartOperationSerializer(serializers.Serializer):
    """Serializer for validating cart operations."""
    product_id = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)

    def validate_product_id(self, value):
        """Validate that the product exists and is available."""
        try:
            product_id = uuid.UUID(str(value))
            product = Product.objects.get(id=product_id)
            if not product.available:
                raise serializers.ValidationError("Product is not available")
            return value
        except (ValueError, Product.DoesNotExist):
            raise serializers.ValidationError("Invalid product ID")

    def validate_quantity(self, value):
        """Validate quantity value."""
        if value is not None and value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        """Validate the entire operation."""
        try:
            product_id = uuid.UUID(str(data['product_id']))
            product = Product.objects.get(id=product_id)
            
            # Get quantity, default to 1 if not provided
            quantity = data.get('quantity', 1)
            
            # Check stock level
            if quantity > product.stock:
                raise serializers.ValidationError({
                    'quantity': f'Requested quantity ({quantity}) exceeds available stock ({product.stock})'
                })
                
            # Add product to validated data for later use
            data['product'] = product
            return data
            
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        except ValueError:
            raise serializers.ValidationError("Invalid product ID format")

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, status='active')
            if not product.available:
                raise serializers.ValidationError("Product is not available")
            if product.stock <= 0:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")

    def validate(self, data):
        """Validate the entire operation."""
        try:
            product = Product.objects.get(id=data['product_id'])
            if data['quantity'] > product.stock:
                raise serializers.ValidationError({
                    "quantity": f"Requested quantity ({data['quantity']}) exceeds available stock ({product.stock})"
                })
        except Product.DoesNotExist:
            pass  # Already handled in validate_product_id
        return data

class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for validating cart item updates."""
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        """Validate quantity value."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
