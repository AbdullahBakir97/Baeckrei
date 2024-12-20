from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ..services.category_service import CategoryService
from ..models import Category

class CategoryController:
    """Controller class for handling category-related business logic."""
    
    def __init__(self):
        self.service = CategoryService()
    
    def get_category_list(self, filters: Dict[str, Any]) -> QuerySet[Category]:
        """Get filtered list of categories."""
        # Start with active categories
        queryset = self.service.get_active_categories()
        
        # Apply search if provided
        search_query = filters.get('search')
        if search_query:
            queryset = self.service.search_categories(search_query)
        
        # Filter by has_products if specified
        has_products = filters.get('has_products')
        if has_products is not None:
            if has_products:
                queryset = self.service.get_categories_with_products()
            else:
                queryset = self.service.get_empty_categories()
        
        return queryset.distinct()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        category = self.service.get_by_id(category_id)
        if not category:
            raise ValidationError(f"Category with ID {category_id} not found")
        return category
    
    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        category = self.service.get_by_slug(slug)
        if not category:
            raise ValidationError(f"Category with slug '{slug}' not found")
        return category
    
    def create_category(self, data: Dict[str, Any]) -> Category:
        """Create a new category."""
        try:
            return self.service.create_category(data)
        except ValidationError as e:
            raise ValidationError(f"Invalid category data: {str(e)}")
    
    def update_category(self, category_id: int, data: Dict[str, Any]) -> Category:
        """Update an existing category."""
        category = self.get_category_by_id(category_id)
        try:
            return self.service.update_category(category, data)
        except ValidationError as e:
            raise ValidationError(f"Invalid category data: {str(e)}")
    
    def delete_category(self, category_id: int) -> None:
        """Delete a category."""
        category = self.get_category_by_id(category_id)
        try:
            self.service.delete(category)
        except Exception as e:
            raise ValidationError(f"Error deleting category: {str(e)}")
    
    def reorder_categories(self, category_orders: List[Dict[str, Any]]) -> None:
        """Reorder categories."""
        try:
            self.service.reorder_categories(category_orders)
        except Exception as e:
            raise ValidationError(f"Error reordering categories: {str(e)}")
    
    def toggle_category_status(self, category_id: int) -> Category:
        """Toggle category active status."""
        category = self.get_category_by_id(category_id)
        try:
            return self.service.toggle_category_status(category)
        except ValidationError as e:
            raise ValidationError(f"Error toggling category status: {str(e)}")
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Get category statistics."""
        try:
            return self.service.get_category_statistics()
        except Exception as e:
            raise ValidationError(f"Error generating category statistics: {str(e)}")
