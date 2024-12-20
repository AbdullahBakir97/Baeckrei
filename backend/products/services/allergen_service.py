from typing import List, Dict, Any, Optional
from django.db.models import QuerySet, Count, Q
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import AllergenInfo
from .base import BaseService

class AllergenService(BaseService[AllergenInfo]):
    """Service for handling allergen-related operations with comprehensive business logic."""
    
    def __init__(self):
        super().__init__(AllergenInfo)
    
    def get_queryset(self) -> QuerySet[AllergenInfo]:
        """Get base queryset with usage counts."""
        return super().get_queryset().annotate(
            ingredient_count=Count('ingredients', distinct=True),
            product_count=Count('ingredients__products', distinct=True)
        )
    
    def get_by_name(self, name: str) -> Optional[AllergenInfo]:
        """Get allergen by exact name match."""
        return self.get_queryset().filter(name__iexact=name).first()
    
    def search_allergens(self, query: str) -> QuerySet[AllergenInfo]:
        """Search allergens by name or description."""
        return self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    
    @transaction.atomic
    def create_allergen(self, data: Dict[str, Any]) -> AllergenInfo:
        """Create an allergen with validation."""
        # Check for duplicate names
        if self.get_by_name(data['name']):
            raise ValidationError(f"Allergen with name '{data['name']}' already exists")
            
        try:
            return super().create(**data)
        except ValidationError as e:
            raise ValidationError(f"Error creating allergen: {str(e)}")
    
    @transaction.atomic
    def update_allergen(self, allergen: AllergenInfo, data: Dict[str, Any]) -> AllergenInfo:
        """Update an allergen with validation."""
        # Check for duplicate names if name is being changed
        if 'name' in data and data['name'] != allergen.name:
            if self.get_by_name(data['name']):
                raise ValidationError(f"Allergen with name '{data['name']}' already exists")
        
        try:
            return super().update(allergen, **data)
        except ValidationError as e:
            raise ValidationError(f"Error updating allergen: {str(e)}")
    
    def get_most_common_allergens(self, limit: int = 10) -> QuerySet[AllergenInfo]:
        """Get most commonly used allergens in products."""
        return self.get_queryset().order_by('-product_count')[:limit]
    
    def get_unused_allergens(self) -> QuerySet[AllergenInfo]:
        """Get allergens not used in any ingredients."""
        return self.get_queryset().filter(ingredient_count=0)
    
    def get_allergens_in_category(self, category_id: int) -> QuerySet[AllergenInfo]:
        """Get allergens used in products of a specific category."""
        return self.get_queryset().filter(
            ingredients__products__category_id=category_id
        ).distinct()
    
    def get_allergen_statistics(self) -> Dict[str, Any]:
        """Get statistics about allergens."""
        queryset = self.get_queryset()
        return {
            'total_allergens': queryset.count(),
            'allergens_in_use': queryset.filter(ingredient_count__gt=0).count(),
            'unused_allergens': queryset.filter(ingredient_count=0).count(),
            'most_common_allergens': list(
                self.get_most_common_allergens(5).values(
                    'id', 'name', 'ingredient_count', 'product_count'
                )
            ),
            'avg_products_per_allergen': queryset.aggregate(
                avg_products=models.Avg('product_count')
            )['avg_products']
        }
    
    @transaction.atomic
    def merge_allergens(self, source_id: int, target_id: int) -> AllergenInfo:
        """Merge one allergen into another."""
        source = self.get_by_id(source_id)
        target = self.get_by_id(target_id)
        
        if not source or not target:
            raise ValidationError("Both source and target allergens must exist")
            
        # Move all ingredients from source to target
        with transaction.atomic():
            # Update all ingredients to use the target allergen
            source.ingredients.all().update(allergens=target)
            # Delete the source allergen
            source.delete()
            
        return target
