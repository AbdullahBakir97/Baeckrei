from typing import List, Dict, Any, Optional, Union
from django.db.models import QuerySet, Count, Q, F
from django.db import transaction
from django.utils.text import slugify
from ..models import Category, Product
from .base import BaseService
from .. import EXCEPTIONS
import uuid

class CategoryService(BaseService[Category]):
    """Service class for managing category-related operations."""

    def __init__(self):
        super().__init__(Category)

    def get_by_id(self, category_id: Union[str, uuid.UUID]) -> Optional[Category]:
        """Get a category by its ID."""
        try:
            return self.with_counts().get(id=category_id)
        except Category.DoesNotExist:
            return None

    def get_category_with_products(self, category_id: Union[str, uuid.UUID]) -> Optional[Category]:
        """Get a category with its products."""
        try:
            return self.with_counts().prefetch_related(
                'products',
                'products__ingredients',
                'products__ingredients__allergens'
            ).filter(id=category_id).first()
        except Category.DoesNotExist:
            return None

    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> Category:
        """Create a category with validation and slug generation."""
        # Validate required fields
        if 'name' not in data:
            raise EXCEPTIONS.ValidationError(
                field='name',
                value=None,
                reason='Name is required for category creation',
                message="Cannot create category: Name is required"
            )

        # Check for duplicate name
        name = data.get('name')
        if self.model.objects.filter(name=name).exists():
            raise EXCEPTIONS.DuplicateCategoryError(
                name=name,
                message=f"Cannot create category: A category with name '{name}' already exists"
            )

        # Generate slug if not provided
        if 'slug' not in data:
            data['slug'] = slugify(data['name'])
            
        # Set default order if not provided
        if 'order' not in data:
            max_order = self.model.objects.aggregate(max_order=F('order').max())['max_order']
            data['order'] = (max_order or 0) + 1
            
        try:
            return self.model.objects.create(**data)
        except EXCEPTIONS.ValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.CategoryError(
                message=f"Error creating category: {str(e)}",
                code="CATEGORY_CREATE_ERROR"
            )

    @transaction.atomic
    def update_category(self, category_id: uuid.UUID, data: Dict[str, Any]) -> Category:
        """Update a category with validation."""
        category = self.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(category_id=category_id)

        # Check for duplicate name if name is being updated
        name = data.get('name')
        if name and self.model.objects.filter(name=name).exclude(id=category.id).exists():
            raise EXCEPTIONS.DuplicateCategoryError(
                name=name,
                message=f"Cannot update category: Another category with name '{name}' already exists"
            )

        # Update slug if name changes
        if 'name' in data and 'slug' not in data:
            data['slug'] = slugify(data['name'])
            
        try:
            for key, value in data.items():
                setattr(category, key, value)
            category.save()
            return category
        except EXCEPTIONS.ValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.CategoryError(
                message=f"Error updating category: {str(e)}",
                code="CATEGORY_UPDATE_ERROR"
            )

    @transaction.atomic
    def delete_category(self, category_id: Union[str, uuid.UUID]) -> None:
        """Delete a category if it has no products."""
        category = self.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(
                category_id=category_id,
                message=f"Cannot delete category: Category with ID '{category_id}' not found"
            )

        # Check if category has products using total_products_count
        if category.total_products_count > 0:
            raise EXCEPTIONS.CategoryInUseError(
                category_id=category_id,
                product_count=category.total_products_count,
                message=(
                    f"Cannot delete category '{category.name}': "
                    f"It contains {category.total_products_count} products. "
                    f"Please reassign or delete the products first"
                )
            )

        try:
            category.delete()
        except Exception as e:
            raise EXCEPTIONS.CategoryError(
                message=f"Error deleting category: {str(e)}",
                code="CATEGORY_DELETE_ERROR"
            )

    @transaction.atomic
    def merge_categories(self, source_id: Union[str, uuid.UUID], target_id: Union[str, uuid.UUID]) -> Category:
        """Merge source category into target category."""
        source = self.get_by_id(source_id)
        target = self.get_by_id(target_id)

        if not source or not target:
            raise EXCEPTIONS.CategoryNotFoundError(
                category_id=source_id if not source else target_id,
                message=f"Cannot merge categories: {'Source' if not source else 'Target'} category not found"
            )

        if source.id == target.id:
            raise EXCEPTIONS.ValidationError(
                field='category_ids',
                value={'source': source_id, 'target': target_id},
                reason='Source and target categories cannot be the same',
                message="Cannot merge a category with itself"
            )

        try:
            return target.merge_with(source)
        except Exception as e:
            raise EXCEPTIONS.CategoryError(
                message=f"Error merging categories: {str(e)}",
                code="CATEGORY_MERGE_ERROR"
            )

    @transaction.atomic
    def reorder_categories(self, order_data: List[Dict[str, Any]]) -> None:
        """Update the display order of categories."""
        categories = []
        for item in order_data:
            category = self.get_by_id(item['id'])
            if category:
                category.order = item['order']
                categories.append(category)
        
        if categories:
            self.model.objects.bulk_update(categories, ['order'])

    @transaction.atomic
    def toggle_status(self, category_id: uuid.UUID) -> Category:
        """Toggle the active status of a category."""
        category = self.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(
                category_id=category_id,
                message="Category not found"
            )
        
        try:
            return category.toggle_status()
        except Exception as e:
            raise EXCEPTIONS.CategoryError(
                message=f"Error toggling category status: {str(e)}",
                code="CATEGORY_STATUS_ERROR"
            )

    def get_filtered_categories(
        self,
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        search_query: Optional[str] = None
    ) -> QuerySet[Category]:
        """
        Get filtered, ordered and searched categories.
        
        Args:
            filters: Dictionary of filter parameters
            ordering: List of fields to order by
            search_query: Optional search term
            
        Returns:
            Filtered queryset with product counts
        """
        return self.model.objects.filter_categories(
            filters=filters,
            search_query=search_query,
            ordering=ordering
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive category statistics."""
        return self.model.objects.get_statistics()
