from django.db import models
from products.models import Product, TimeStampedModel
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Customer

Customer = Customer

class Cart(TimeStampedModel):
    """Model representing a shopping cart."""
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        blank=True
    )
    session = models.CharField(max_length=40, null=True, blank=True)
    _total_items = models.IntegerField(default=0, db_column='total_items')
    _subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='subtotal'
    )
    _tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='tax'
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
        return self._total_items

    @property
    def subtotal(self):
        return self._subtotal

    @property
    def tax(self):
        return self._tax

    @property
    def total(self):
        return self.subtotal + self.tax

    def add_item(self, product: Product, quantity: int = 1) -> 'CartItem':
        """Add a product to cart or update if exists."""
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.price
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        self.update_totals()
        return cart_item

    def remove_item(self, product: Product) -> None:
        """Remove a product from cart."""
        self.items.filter(product=product).delete()
        self.update_totals()

    def update_item(self, product: Product, quantity: int) -> 'CartItem':
        """Update quantity of an item in cart."""
        cart_item = self.items.filter(product=product).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()
            self.update_totals()
            return cart_item
        raise CartNotFoundError(f"Product {product.id} not found in cart")

    def clear(self) -> None:
        """Remove all items from cart."""
        self.items.all().delete()
        self.update_totals()

    def update_totals(self) -> None:
        """Update cart totals."""
        self._total_items = sum(item.quantity for item in self.items.all())
        self._subtotal = sum(item.total_price for item in self.items.all())
        self._tax = Decimal('0.10') * self._subtotal  # 10% tax
        self.save()

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
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart {self.cart.id}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
        else:
            super().save(*args, **kwargs)

class CartNotFoundError(Exception):
    pass
