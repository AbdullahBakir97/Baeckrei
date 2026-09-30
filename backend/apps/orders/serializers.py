from django.conf import settings
from django.utils import timezone
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
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'transaction_id', 'status', 'payment_date',
            'created_at', 'updated_at'
        ]

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
    address = AddressSerializer(required=False, allow_null=True)
    payment = PaymentSerializer(source='order_payment', read_only=True)
    fulfillment_display = serializers.CharField(source='get_fulfillment_method_display', read_only=True)
    vat_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'status', 'status_display', 'total_price', 'vat_amount', 'items',
            'fulfillment_method', 'fulfillment_display', 'delivery_fee',
            'address', 'contact_phone', 'requested_time', 'shipping_tracking_number',
            'estimated_delivery_date', 'notes', 'created_at',
            'updated_at', 'total_items', 'payment',
            'is_cancelable', 'is_overdue'
        ]
        # Ownership, status and fulfilment fields are managed server-side
        # (status/tracking via the staff-only actions), never by the client.
        read_only_fields = [
            'order_number', 'customer', 'status', 'total_price',
            'fulfillment_method', 'delivery_fee', 'requested_time',
            'shipping_tracking_number', 'estimated_delivery_date',
            'created_at', 'updated_at', 'total_items', 'is_cancelable',
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


class CheckoutAddressSerializer(serializers.Serializer):
    address_line_1 = serializers.CharField(max_length=255)
    address_line_2 = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    country = serializers.CharField(max_length=100, required=False, default='DE')


class CheckoutSerializer(serializers.Serializer):
    """Input for turning the current cart into an order."""
    fulfillment_method = serializers.ChoiceField(choices=Order.FulfillmentChoices.choices)
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)
    address = CheckoutAddressSerializer(required=False)
    address_id = serializers.IntegerField(required=False)
    contact_phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default='')
    requested_time = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if attrs['fulfillment_method'] == Order.FulfillmentChoices.DELIVERY:
            if not attrs.get('address') and not attrs.get('address_id'):
                raise serializers.ValidationError({'address': 'A delivery address is required.'})
        if attrs['payment_method'] == Payment.PaymentMethod.PAYPAL and not settings.PAYPAL_ENABLED:
            raise serializers.ValidationError({'payment_method': 'PayPal is not available yet.'})
        requested_time = attrs.get('requested_time')
        if requested_time and requested_time < timezone.now():
            raise serializers.ValidationError({'requested_time': 'Choose a time in the future.'})
        return attrs

