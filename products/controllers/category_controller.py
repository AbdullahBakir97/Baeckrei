from typing import Dict, Any, Optional
from django.db.models import QuerySet
from ..services.category_service import CategoryService
from ..models import Category

class CategoryController:
    """Controller for handling category-related operations."""
    
    def __init__(self):
        self.service = CategoryService()
    
    def get_category_list(self, filters: Dict[str, Any]) -> QuerySet[Category]:
        """Get filtered list of categories."""
        queryset = self.service.get_active_categories()
        
        # Apply search if provided
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset
    
    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return self.service.get_by_slug(slug)
    
    def create_category(self, data: Dict[str, Any]) -> Category:
        """Create a new category."""
        return self.service.create_category(**data)
    
    def update_category(self, category: Category, data: Dict[str, Any]) -> Category:
        """Update an existing category."""
        return self.service.update_category(category, **data)
    
    def delete_category(self, category: Category) -> None:
        """Delete a category."""
        self.service.delete(category)
    
    def reorder_categories(self, order_mapping: Dict[str, int]) -> None:
        """Reorder categories."""
        self.service.reorder_categories(order_mapping)
