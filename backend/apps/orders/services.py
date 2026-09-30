from decimal import Decimal
from django.utils.translation import gettext as _
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import Order, OrderItem, Payment
from apps.products.models import Product
from apps.accounts.models import Customer, Address


class CheckoutError(Exception):
    """A checkout that cannot be completed; the message is shown to the customer."""

    def __init__(self, message, code='checkout_error', extra=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.extra = extra or {}

class OrderService:
    ALLOWED_STATUS_TRANSITIONS = {
        Order.StatusChoices.PENDING: {Order.StatusChoices.PROCESSING, Order.StatusChoices.CANCELED},
        Order.StatusChoices.PROCESSING: {Order.StatusChoices.COMPLETED, Order.StatusChoices.CANCELED},
        Order.StatusChoices.COMPLETED: set(),
        Order.StatusChoices.CANCELED: set(),
    }

    @staticmethod
    @transaction.atomic
    def create_order(customer: Customer, items: list, address_data: dict, notes: str = None) -> Order:
        """Create a new order with items"""
        order = Order.objects.create(
            customer=customer,
            status=Order.StatusChoices.PENDING,
            notes=notes
        )
        
        # Create address and link to order
        order.update_shipping_address(address_data)
        
        # Add items to order
        for item_data in items:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price_per_item=product.price
            )
        
        order.recalculate_total()
        return order

    @staticmethod
    def checkout(customer: Customer, cart, data: dict, language: str = 'de') -> Order:
        """Turn the customer's cart into an order.

        Stock is deducted here (and only here), atomically per product, so two
        customers cannot both buy the last item. Orders paid on pickup or
        delivery are confirmed by email right away; online payments once
        Stripe reports them paid (see payments.py).
        """
        from . import emails
        from apps.cart.models import Cart

        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(pk=cart.pk)
            if cart.completed:
                raise CheckoutError(_('This cart has already been checked out.'), 'cart_completed')

            items = [item for item in cart.items.select_related('product') if item.product_id]
            if not items:
                raise CheckoutError(_('Your cart is empty.'), 'empty_cart')

            for item in items:
                product = item.product
                if not product.available or product.status != 'active':
                    raise CheckoutError(
                        _('{name} is no longer available.').format(name=product.name), 'unavailable',
                        {'product_id': str(product.pk)},
                    )
                updated = Product.objects.filter(pk=product.pk, stock__gte=item.quantity).update(
                    stock=F('stock') - item.quantity
                )
                if not updated:
                    available = Product.objects.filter(pk=product.pk).values_list('stock', flat=True).first() or 0
                    raise CheckoutError(
                        _('Only {count} × {name} left in stock.').format(count=available, name=product.name), 'insufficient_stock',
                        {'product_id': str(product.pk), 'available_stock': available},
                    )

            is_delivery = data['fulfillment_method'] == Order.FulfillmentChoices.DELIVERY
            address = None
            if is_delivery:
                if data.get('address_id'):
                    address = Address.objects.filter(pk=data['address_id'], customer=customer).first()
                    if address is None:
                        raise CheckoutError(_('That address could not be found.'), 'invalid_address')
                else:
                    address = Address.objects.create(
                        customer=customer, saved=data.get('save_address', False), **data['address']
                    )

            requested_time = data.get('requested_time')
            order = Order.objects.create(
                customer=customer,
                address=address,
                fulfillment_method=data['fulfillment_method'],
                delivery_fee=settings.DELIVERY_FEE if is_delivery else Decimal('0.00'),
                contact_phone=data.get('contact_phone', ''),
                requested_time=requested_time,
                estimated_delivery_date=(requested_time or timezone.now()).date(),
                notes=data.get('notes', ''),
                language=language if language in dict(settings.LANGUAGES) else 'de',
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=item.product, quantity=item.quantity,
                          price_per_item=item.product.price)
                for item in items
            ])
            order.save()  # recompute total_price from the items and delivery fee

            payment = Payment.objects.create(
                order=order,
                payment_method=data['payment_method'],
                amount=order.total_price,
            )
            Cart.objects.filter(pk=cart.pk).update(completed=True, completed_at=timezone.now())
            if not payment.is_online:
                transaction.on_commit(lambda: emails.order_placed(order))
            return order

    @staticmethod
    def update_order_status(order: Order, new_status: str, reason: str = '') -> Order:
        """Change an order's status. Canceling gives the stock back, refunds an
        online payment (or closes its unpaid payment page) and tells the
        customer by email, with `reason` if given."""
        from . import emails, payments
        if new_status not in Order.StatusChoices.values:
            raise ValueError(f"Invalid status: {new_status}")

        if new_status not in OrderService.ALLOWED_STATUS_TRANSITIONS.get(order.status, set()):
            raise ValueError(f"Cannot change order status from {order.status} to {new_status}")

                
        payment = getattr(order, 'order_payment', None)
        with transaction.atomic():
            if new_status == Order.StatusChoices.CANCELED:
                # Stock was deducted at checkout; put it back.
                for item in order.order_items.all():
                    Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
                if payment and payment.is_online:
                    if payment.status == Payment.PaymentStatus.COMPLETED:
                        # Raises PaymentError (and keeps the order) if Stripe refuses.
                        payments.refund(payment)
                    elif payment.status == Payment.PaymentStatus.PENDING:
                        payments.expire_checkout(payment)
                        payment.record_failure(reason or 'Order canceled before payment')
                transaction.on_commit(lambda: emails.order_canceled(order, reason))
            order.status = new_status
            order.save()
            # Cash and card are paid when the order is handed over.
            if (new_status == Order.StatusChoices.COMPLETED and payment
                    and payment.status == Payment.PaymentStatus.PENDING
                    and payment.payment_method in (Payment.PaymentMethod.CASH, Payment.PaymentMethod.CREDIT_CARD)):
                payment.complete_payment()
        return order

    @staticmethod
    def add_tracking_number(order: Order, tracking_number: str) -> Order:
        """Add shipping tracking number to order"""
        order.shipping_tracking_number = tracking_number
        order.save()
        return order