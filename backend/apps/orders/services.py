from decimal import Decimal
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
    def checkout(customer: Customer, cart, data: dict) -> Order:
        """Turn the customer's cart into an order.

        Stock is deducted here (and only here), atomically per product, so two
        customers cannot both buy the last item.
        """
        from apps.cart.models import Cart

        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(pk=cart.pk)
            if cart.completed:
                raise CheckoutError('This cart has already been checked out.', 'cart_completed')

            items = [item for item in cart.items.select_related('product') if item.product_id]
            if not items:
                raise CheckoutError('Your cart is empty.', 'empty_cart')

            for item in items:
                product = item.product
                if not product.available or product.status != 'active':
                    raise CheckoutError(
                        f'{product.name} is no longer available.', 'unavailable',
                        {'product_id': str(product.pk)},
                    )
                updated = Product.objects.filter(pk=product.pk, stock__gte=item.quantity).update(
                    stock=F('stock') - item.quantity
                )
                if not updated:
                    available = Product.objects.filter(pk=product.pk).values_list('stock', flat=True).first() or 0
                    raise CheckoutError(
                        f'Only {available} × {product.name} left in stock.', 'insufficient_stock',
                        {'product_id': str(product.pk), 'available_stock': available},
                    )

            is_delivery = data['fulfillment_method'] == Order.FulfillmentChoices.DELIVERY
            address = None
            if is_delivery:
                if data.get('address_id'):
                    address = Address.objects.filter(pk=data['address_id'], customer=customer).first()
                    if address is None:
                        raise CheckoutError('That address could not be found.', 'invalid_address')
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
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=item.product, quantity=item.quantity,
                          price_per_item=item.product.price)
                for item in items
            ])
            order.save()  # recompute total_price from the items and delivery fee

            Payment.objects.create(
                order=order,
                payment_method=data['payment_method'],
                amount=order.total_price,
            )
            Cart.objects.filter(pk=cart.pk).update(completed=True, completed_at=timezone.now())
            return order

    @staticmethod
    def update_order_status(order: Order, new_status: str) -> Order:
        """Update order status with validation"""
        if new_status not in Order.StatusChoices.values:
            raise ValueError(f"Invalid status: {new_status}")

        if new_status not in OrderService.ALLOWED_STATUS_TRANSITIONS.get(order.status, set()):
            raise ValueError(f"Cannot change order status from {order.status} to {new_status}")

        if new_status == Order.StatusChoices.COMPLETED:
            if not order.shipping_tracking_number:
                raise ValueError("Cannot complete order without tracking number")
                
        with transaction.atomic():
            if new_status == Order.StatusChoices.CANCELED:
                # Stock was deducted at checkout; put it back.
                for item in order.order_items.all():
                    Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
            order.status = new_status
            order.save()
        return order

    @staticmethod
    def add_tracking_number(order: Order, tracking_number: str) -> Order:
        """Add shipping tracking number to order"""
        order.shipping_tracking_number = tracking_number
        order.save()
        return order