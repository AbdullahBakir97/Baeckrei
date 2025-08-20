"""Product factories for testing."""
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from .models import Product

class ProductFactory(DjangoModelFactory):
    """Factory for creating test products."""

    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Test Product {n}')
    description = factory.Sequence(lambda n: f'Test Description {n}')
    price = Decimal('10.00')
    stock = 10
    available = True
    status = 'active'
    version = 1
