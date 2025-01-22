from decimal import Decimal
from django.db import transaction
from ..models import Order, OrderItem
from products.models import Product
from accounts.models import Customer, Address

class OrderService:
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
    def update_order_status(order: Order, new_status: str) -> Order:
        """Update order status with validation"""
        if new_status not in Order.StatusChoices.values:
            raise ValueError(f"Invalid status: {new_status}")
            
        if new_status == Order.StatusChoices.COMPLETED:
            if not order.shipping_tracking_number:
                raise ValueError("Cannot complete order without tracking number")
                
        order.status = new_status
        order.save()
        return order

    @staticmethod
    def add_tracking_number(order: Order, tracking_number: str) -> Order:
        """Add shipping tracking number to order"""
        order.shipping_tracking_number = tracking_number
        order.save()
        return order