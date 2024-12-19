from typing import Optional, List
from django.db.models import QuerySet
from ..models import Product, Category
from .base import BaseService

class ProductService(BaseService[Product]):
    """Service class for Product-related operations."""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_queryset(self) -> QuerySet[Product]:
        """Get the base queryset with related fields."""
        return super().get_queryset().select_related(
            'category', 
            'nutrition_info'
        ).prefetch_related('ingredients', 'ingredients__allergens')
    
    def get_available_products(self) -> QuerySet[Product]:
        """Get all available products."""
        return self.get_queryset().available()
    
    def get_featured_products(self, limit: int = 6) -> QuerySet[Product]:
        """Get featured products."""
        return self.get_available_products().order_by('-created_at')[:limit]
    
    def get_by_category(self, category: Category) -> QuerySet[Product]:
        """Get products by category."""
        return self.get_available_products().filter(category=category)
    
    def filter_by_dietary_preferences(
        self, 
        vegan: bool = False, 
        vegetarian: bool = False, 
        gluten_free: bool = False
    ) -> QuerySet[Product]:
        """Filter products by dietary preferences."""
        return self.get_queryset().dietary_preferences(
            vegan=vegan,
            vegetarian=vegetarian,
            gluten_free=gluten_free
        )
    
    def search_products(
        self, 
        query: str,
        category_slug: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        **dietary_filters
    ) -> QuerySet[Product]:
        """
        Search products with various filters.
        
        Args:
            query: Search query string
            category_slug: Optional category slug to filter by
            min_price: Optional minimum price
            max_price: Optional maximum price
            **dietary_filters: Dietary preference filters (vegan, vegetarian, gluten_free)
        """
        queryset = self.get_available_products()
        
        if query:
            queryset = queryset.filter(name__icontains=query)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        if any(dietary_filters.values()):
            queryset = self.filter_by_dietary_preferences(**dietary_filters)
        
        return queryset
    
    def create_product(
        self,
        name: str,
        category: Category,
        price: float,
        description: str,
        **additional_data
    ) -> Product:
        """
        Create a new product with validation.
        
        Args:
            name: Product name
            category: Product category
            price: Product price
            description: Product description
            **additional_data: Additional product data
        """
        # Generate slug if not provided
        if 'slug' not in additional_data:
            from django.utils.text import slugify
            additional_data['slug'] = slugify(name)
        
        return self.create(
            name=name,
            category=category,
            price=price,
            description=description,
            **additional_data
        )
    
    def update_product(
        self,
        product: Product,
        **data
    ) -> Product:
        """
        Update a product with validation.
        
        Args:
            product: Product instance to update
            **data: Updated product data
        """
        if 'name' in data and 'slug' not in data:
            from django.utils.text import slugify
            data['slug'] = slugify(data['name'])
        
        return self.update(product, **data)
    
    def toggle_availability(self, product: Product) -> Product:
        """Toggle product availability status."""
        product.available = not product.available
        product.save()
        return product
