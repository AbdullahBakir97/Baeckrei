from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Count, F
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from ..models import Category
from .base import BaseService

class CategoryService(BaseService[Category]):
    """Service class for Category-related operations with comprehensive business logic."""
    
    def __init__(self):
        super().__init__(Category)
    
    def get_queryset(self) -> QuerySet[Category]:
        """Get the base queryset with product count annotation."""
        return super().get_queryset().annotate(
            product_count=Count('products', distinct=True)
        ).order_by('order', 'name')
    
    def get_active_categories(self) -> QuerySet[Category]:
        """Get all active categories with product counts."""
        return self.get_queryset().filter(is_active=True)
    
    def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug with validation."""
        return self.get_queryset().filter(slug=slug).first()
    
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> Category:
        """Create a category with validation and slug generation."""
        # Generate slug if not provided
        if 'slug' not in data:
            data['slug'] = slugify(data['name'])
            
        # Set default order if not provided
        if 'order' not in data:
            max_order = self.get_queryset().aggregate(max_order=F('order').max())['max_order']
            data['order'] = (max_order or 0) + 1
            
        try:
            return super().create(**data)
        except ValidationError as e:
            raise ValidationError(f"Error creating category: {str(e)}")
    
    @transaction.atomic
    def update_category(self, category: Category, data: Dict[str, Any]) -> Category:
        """Update a category with validation."""
        # Update slug if name changes
        if 'name' in data and 'slug' not in data:
            data['slug'] = slugify(data['name'])
            
        try:
            return super().update(category, **data)
        except ValidationError as e:
            raise ValidationError(f"Error updating category: {str(e)}")
    
    @transaction.atomic
    def reorder_categories(self, category_orders: List[Dict[str, Any]]) -> None:
        """Reorder categories by updating their order values."""
        with transaction.atomic():
            for item in category_orders:
                Category.objects.filter(id=item['id']).update(order=item['order'])
    
    def get_categories_with_products(self) -> QuerySet[Category]:
        """Get active categories that have products."""
        return self.get_active_categories().filter(product_count__gt=0)
    
    def get_empty_categories(self) -> QuerySet[Category]:
        """Get categories without products."""
        return self.get_active_categories().filter(product_count=0)
    
    @transaction.atomic
    def toggle_category_status(self, category: Category) -> Category:
        """Toggle category active status with validation."""
        if category.product_count > 0 and category.is_active:
            raise ValidationError("Cannot deactivate category with active products")
            
        return self.update(category, is_active=not category.is_active)
    
    def search_categories(self, query: str) -> QuerySet[Category]:
        """Search categories by name or description."""
        from django.db.models import Q
        return self.get_active_categories().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Get statistics about categories."""
        queryset = self.get_queryset()
        from django.db.models import Avg
        return {
            'total_categories': queryset.count(),
            'active_categories': queryset.filter(is_active=True).count(),
            'categories_with_products': queryset.filter(product_count__gt=0).count(),
            'empty_categories': queryset.filter(product_count=0).count(),
            'avg_products_per_category': queryset.filter(is_active=True).aggregate(
                avg_products=Avg('product_count')
            )['avg_products']
        }
