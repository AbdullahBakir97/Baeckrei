from django.db import models
from products.models import Product, TimeStampedModel
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Customer

Customer = Customer

class Cart(TimeStampedModel):
    """Model representing a shopping cart."""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.id} - {self.customer}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def tax(self):
        return Decimal('0.10') * self.subtotal  # 10% tax

    @property
    def total(self):
        return self.subtotal + self.tax

    def add_item(self, product, quantity=1):
        """Add a product to cart or update its quantity if it already exists."""
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def update_item(self, product, quantity):
        """Update the quantity of a product in cart."""
        try:
            cart_item = self.items.get(product=product)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
            return cart_item
        except CartItem.DoesNotExist:
            return None

    def remove_item(self, product):
        """Remove a product from cart."""
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()

class CartItem(TimeStampedModel):
    """Model representing an item in a shopping cart."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart {self.cart.id}"

    @property
    def unit_price(self):
        return self.product.price

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
        else:
            super().save(*args, **kwargs)
