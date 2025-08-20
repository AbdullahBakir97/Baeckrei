from rest_framework import serializers
from .models import Order, OrderItem, Payment
from apps.accounts.models import Address
from apps.accounts.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image',
            'quantity', 'price_per_item', 'subtotal'
        ]
        read_only_fields = ['price_per_item', 'subtotal']

class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method',
            'payment_method_display', 'transaction_id',
            'status', 'status_display', 'payment_date',
            'last_four', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'transaction_id', 'status', 'payment_date',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'last_four': {'write_only': True}
        }

    def validate_amount(self, value):
        """Validate payment amount matches order total"""
        order = self.instance.order if self.instance else self.initial_data.get('order')
        if order and value != order.total_price:
            raise serializers.ValidationError(
                "Payment amount must match order total"
            )
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='order_items', many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    address = AddressSerializer()
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'status', 'status_display', 'total_price', 'items',
            'address', 'shipping_tracking_number',
            'estimated_delivery_date', 'notes', 'created_at',
            'updated_at', 'total_items', 'payments',
            'is_cancelable', 'is_overdue'
        ]
        read_only_fields = [
            'order_number', 'total_price', 'created_at',
            'updated_at', 'total_items', 'is_cancelable',
            'is_overdue'
        ]

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        order = Order.objects.create(**validated_data)
        order.update_shipping_address(address_data)
        return order

    def update(self, instance, validated_data):
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            instance.update_shipping_address(address_data)
        return super().update(instance, validated_data)

class OrderCreateSerializer(OrderSerializer):
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        write_only=True
    )

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        address_data = validated_data.pop('address')
        
        order = Order.objects.create(**validated_data)
        order.update_shipping_address(address_data)

        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
        
        order.recalculate_total()
        return order