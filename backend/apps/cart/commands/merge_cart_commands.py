"""Cart merge command implementation."""
from typing import Optional
from django.db import transaction
from .base import BaseCommand
from ..models import Cart
from ..strategies.cart_strategies import MergeCartStrategy

class MergeCartsCommand(BaseCommand):
    """Command for merging guest cart into customer cart."""
    
    def __init__(self, customer_cart: Cart, guest_cart: Cart):
        strategy = MergeCartStrategy(customer_cart)
        super().__init__(customer_cart, strategy)
        self.guest_cart = guest_cart
        
    def _execute(self) -> None:
        """Execute cart merge."""
        with transaction.atomic():
            self.strategy.execute(self.guest_cart)
            self.guest_cart.delete()