from functools import cache
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, F, Q
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import Product, Category
from .base import BaseService
import uuid

from products import models

class ProductService(BaseService[Product]):
    """Service class for Product-related operations with business logic."""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_queryset(self) -> QuerySet[Product]:
        """Get the base queryset with related fields."""
        return super().get_queryset().select_related(
            'category', 
            'nutrition_info'
        ).prefetch_related('ingredients', 'ingredients__allergens')
    
    def get_available_products(self, category_id: Optional[uuid.UUID] = None) -> QuerySet[Product]:
        """Get all available products, optionally filtered by category."""
        queryset = self.get_queryset().filter(
            status='active',
            available=True,
            stock__gt=0
        )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def get_featured_products(self, limit: int = 6) -> QuerySet[Product]:
        """Get featured products."""
        return self.get_available_products().order_by('-created_at')[:limit]
    
    def get_by_category(self, category: Category) -> QuerySet[Product]:
        """Get products by category."""
        return self.get_available_products(category.id)
    
    @transaction.atomic
    def update_stock(self, product_id: uuid.UUID, quantity_change: int) -> Product:
        """Update product stock with validation."""
        product = self.get_by_id(product_id)
        if not product:
            raise ValidationError("Product not found")
        
        new_stock = F('stock') + quantity_change
        
        # Prevent negative stock
        if quantity_change < 0:
            product.refresh_from_db()
            if product.stock + quantity_change < 0:
                raise ValidationError("Insufficient stock")
        
        Product.objects.filter(id=product_id).update(stock=new_stock)
        product.refresh_from_db()
        
        # Auto-update availability based on stock
        if product.stock == 0 and product.available:
            self.update(product, available=False)
        elif product.stock > 0 and not product.available:
            self.update(product, available=True)
        
        return product
    
    def search_products(self, query: str) -> QuerySet[Product]:
        """Search products by name, description, or category."""
        return self.get_available_products().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    def get_products_by_allergens(self, exclude_allergens: List[uuid.UUID]) -> QuerySet[Product]:
        """Get products excluding specific allergens."""
        return self.get_available_products().exclude(
            ingredients__allergens__id__in=exclude_allergens
        )
    
    def get_products_by_dietary_preferences(self, 
                                         is_vegan: bool = False,
                                         is_vegetarian: bool = False,
                                         is_gluten_free: bool = False) -> QuerySet[Product]:
        """Get products matching dietary preferences."""
        filters = {}
        if is_vegan:
            filters['is_vegan'] = True
        if is_vegetarian:
            filters['is_vegetarian'] = True
        if is_gluten_free:
            filters['is_gluten_free'] = True
        return self.get_available_products().filter(**filters)
    
    @transaction.atomic
    def create_product(self, data: Dict[str, Any]) -> Product:
        """Create a product with additional validation and processing."""
        # Extract many-to-many relationships
        ingredients = data.pop('ingredients', [])
        
        # Create the product
        product = super().create(**data)
        
        # Add ingredients
        if ingredients:
            product.ingredients.set(ingredients)
        
        return product
    
    @transaction.atomic
    def update_product(self, product: Product, data: Dict[str, Any]) -> Product:
        """Update a product with additional validation and processing."""
        # Extract many-to-many relationships
        ingredients = data.pop('ingredients', None)
        
        # Update the product
        product = super().update(product, **data)
        
        # Update ingredients if provided
        if ingredients is not None:
            product.ingredients.set(ingredients)
        
        return product
    
    def bulk_update_prices(self, price_updates: List[dict]) -> None:
        """
        Bulk update product prices.
        Args:
            price_updates: List of dictionaries with 'id' and 'price' keys.
        """
        products = [self.get_by_id(update['id']) for update in price_updates]
        for product, update in zip(products, price_updates):
            product.price = update['price']
        self.bulk_update(products, ['price'])
    
    def generate_report(self) -> dict:
        """Generate a summary report of products."""
        queryset = self.get_queryset()
        return {
            'total_products': queryset.count(),
            'active_products': queryset.filter(status='active').count(),
            'discontinued_products': queryset.filter(status='discontinued').count(),
            'average_price': queryset.aggregate(models.Avg('price'))['price__avg'],
            'total_stock': queryset.aggregate(models.Sum('stock'))['stock__sum']
        }

    @staticmethod
    def get_product(product_id):
        """Retrieve a product with caching."""
        cache_key = f"product_{product_id}"
        product = cache.get(cache_key)
        if not product:
            product = Product.objects.get(id=product_id)
            cache.set(cache_key, product, timeout=300)  # Cache for 5 minutes
        return product

    @staticmethod
    def get_all_products():
        """Retrieve all products with caching."""
        cache_key = "all_products"
        products = cache.get(cache_key)
        if not products:
            products = list(Product.objects.all())
            cache.set(cache_key, products, timeout=300)
        return products
