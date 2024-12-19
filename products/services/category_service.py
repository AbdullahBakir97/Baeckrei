from typing import Optional
from django.db.models import QuerySet, Count
from ..models import Category
from .base import BaseService

class CategoryService(BaseService[Category]):
    """Service class for Category-related operations."""
    
    def __init__(self):
        super().__init__(Category)
    
    def get_queryset(self) -> QuerySet[Category]:
        """Get the base queryset with product count annotation."""
        return super().get_queryset().annotate(
            product_count=Count('products')
        ).filter(is_active=True).order_by('order', 'name')
    
    def get_active_categories(self) -> QuerySet[Category]:
        """Get all active categories."""
        return self.get_queryset().filter(is_active=True)
    
    def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return self.get_queryset().filter(slug=slug).first()
    
    def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        order: Optional[int] = None,
        **additional_data
    ) -> Category:
        """
        Create a new category with validation.
        
        Args:
            name: Category name
            description: Optional category description
            order: Optional display order
            **additional_data: Additional category data
        """
        # Generate slug if not provided
        if 'slug' not in additional_data:
            from django.utils.text import slugify
            additional_data['slug'] = slugify(name)
        
        # Set default order if not provided
        if order is None:
            last_order = self.get_queryset().order_by('-order').first()
            order = (last_order.order + 1) if last_order else 1
        
        return self.create(
            name=name,
            description=description,
            order=order,
            **additional_data
        )
    
    def update_category(
        self,
        category: Category,
        **data
    ) -> Category:
        """
        Update a category with validation.
        
        Args:
            category: Category instance to update
            **data: Updated category data
        """
        if 'name' in data and 'slug' not in data:
            from django.utils.text import slugify
            data['slug'] = slugify(data['name'])
        
        return self.update(category, **data)
    
    def reorder_categories(self, order_mapping: dict) -> None:
        """
        Reorder categories based on provided mapping.
        
        Args:
            order_mapping: Dict mapping category IDs to new order values
        """
        for category_id, new_order in order_mapping.items():
            category = self.get_by_id(category_id)
            self.update(category, order=new_order)
    
    def toggle_active_status(self, category: Category) -> Category:
        """Toggle category active status."""
        category.is_active = not category.is_active
        category.save()
        return category
