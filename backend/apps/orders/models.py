from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.accounts.models import Customer, Address
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.conf import settings


def vat_included(gross: Decimal) -> Decimal:
    """VAT contained in a gross (VAT-inclusive) amount."""
    rate = Decimal(str(getattr(settings, 'VAT_RATE', '0.19')))
    gross = Decimal(gross or 0)
    return (gross - gross / (1 + rate)).quantize(Decimal('0.01'))


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        PROCESSING = 'Processing', _('Processing')
        COMPLETED = 'Completed', _('Completed')
        CANCELED = 'Canceled', _('Canceled')

    class FulfillmentChoices(models.TextChoices):
        PICKUP = 'pickup', _('Pickup')
        DELIVERY = 'delivery', _('Delivery')

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        editable=False
    )
    fulfillment_method = models.CharField(
        max_length=10,
        choices=FulfillmentChoices.choices,
        default=FulfillmentChoices.PICKUP,
    )
    # Only delivery orders have an address; pickup orders are collected in the shop.
    address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name='order_addresses', null=True, blank=True
    )
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    contact_phone = models.CharField(max_length=30, blank=True, default='')
    requested_time = models.DateTimeField(null=True, blank=True)
    shipping_tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        if not self.estimated_delivery_date:
            self.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=5)
        
        if self.pk:
            items_total = sum((item.subtotal for item in self.order_items.all()), Decimal('0.00'))
            self.total_price = items_total + (self.delivery_fee or Decimal('0.00'))
        else:
            self.total_price = Decimal('0.00')
            
        super().save(*args, **kwargs)

    @property
    def vat_amount(self):
        """VAT included in the total (prices are gross)."""
        return vat_included(self.total_price)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    @property
    def is_cancelable(self):
        return self.status in [self.StatusChoices.PENDING, self.StatusChoices.PROCESSING]

    @property
    def order_age(self):
        return timezone.now() - self.created_at
    
    @property
    def is_overdue(self):
        return self.status == self.StatusChoices.PROCESSING and self.order_age.days > 7

    def clean(self):
        total = self.total_price or 0
        if total < 0:
            raise ValidationError(_('Total price cannot be negative.'))
        if self.status == self.StatusChoices.COMPLETED and not self.shipping_tracking_number:
            raise ValidationError(_('Shipping tracking number is required for completed orders.'))
        if self.fulfillment_method == self.FulfillmentChoices.DELIVERY and not self.address:
            raise ValidationError(_('Delivery orders need an address'))

    def update_shipping_address(self, address_data):
        """Update or set shipping address for the order"""
        if not self.address:
            self.address = Address.objects.create(**address_data)
        else:
            for key, value in address_data.items():
                setattr(self.address, key, value)
            self.address.save()
        self.save()

    def calculate_order_total(order_items):
        """Calculate the total price for an order."""
        total = 0
        for item in order_items:
            total += item.quantity * item.price_per_item
        return total

    def recalculate_total(self):
        self.total_price = self.order_items.aggregate(
            total=Sum(models.F('quantity') * models.F('price_per_item'))
        )['total'] or Decimal('0.00')
        self.save()

    def process_order(self):
        self.status = self.StatusChoices.PROCESSING
        self.save()

    def complete_order(self):
        self.status = self.StatusChoices.COMPLETED
        self.save()

    def cancel_order(self):
        self.status = self.StatusChoices.CANCELED
        self.save()

    def __str__(self):
        return f"Order #{self.order_number} for {self.customer.name}"

Order._meta.constraints = [
    models.CheckConstraint(
        condition=models.Q(status__in=[choice[0] for choice in Order.StatusChoices.choices]),
        name='valid_order_status'
    )
]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='order_items_product')
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )

    class Meta:
        ordering = ['id']

    @property
    def subtotal(self):
        if self.quantity is None or self.price_per_item is None:
            return 0
        return self.quantity * self.price_per_item

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(_('Quantity must be greater than zero'))
        if hasattr(self.product, 'stock') and self.quantity > self.product.stock:
            raise ValidationError(_('Not enough stock available'))

    def update_stock(self):
        with transaction.atomic():
            self.product.stock = models.F('stock') - self.quantity
            self.product.save()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.order_number})"

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'CC', _('Credit Card')
        PAYPAL = 'PP', _('PayPal')
        # BANK_TRANSFER = 'BT', _('Bank Transfer')
        CASH = 'CA', _('Cash')

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        COMPLETED = 'Completed', _('Completed')
        FAILED = 'Failed', _('Failed')
        REFUNDED = 'Refunded', _('Refunded')

    payment_method = models.CharField(
        max_length=2,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PAYPAL,
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_payment')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    payment_gateway_response = models.JSONField(null=True, blank=True)
    failure_reason = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
        ]

    def clean(self):
        if self.amount != self.order.total_price:
            raise ValidationError(_('Payment amount must match order total'))

    @property
    def is_refundable(self):
        return self.status == self.PaymentStatus.COMPLETED

    def complete_payment(self):
        self.status = self.PaymentStatus.COMPLETED
        self.payment_date = timezone.now()
        self.is_verified = True
        self.save()

    def fail_payment(self):
        self.status = self.PaymentStatus.FAILED
        self.save()

    def refund_payment(self):
        if self.status != self.PaymentStatus.COMPLETED:
            raise ValidationError(_('Only completed payments can be refunded'))
        self.status = self.PaymentStatus.REFUNDED
        self.save()

    def record_failure(self, reason):
        self.status = self.PaymentStatus.FAILED
        self.failure_reason = reason
        self.save()

    def __str__(self):
        return f"Payment for Order #{self.order.order_number}"
