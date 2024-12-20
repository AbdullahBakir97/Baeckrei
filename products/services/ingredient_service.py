from typing import List, Dict, Any, Optional
from django.db.models import QuerySet, Count, Q
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import Ingredient, AllergenInfo
from .base import BaseService

class IngredientService(BaseService[Ingredient]):
    """Service for handling ingredient-related operations with comprehensive business logic."""
    
    def __init__(self):
        super().__init__(Ingredient)
    
    def get_queryset(self) -> QuerySet[Ingredient]:
        """Get base queryset with related fields and usage count."""
        return super().get_queryset().prefetch_related(
            'allergens', 'products'
        ).annotate(
            usage_count=Count('products', distinct=True)
        )
    
    def get_active_ingredients(self) -> QuerySet[Ingredient]:
        """Get all active ingredients with their usage information."""
        return self.get_queryset().filter(is_active=True)
    
    def get_by_allergen(self, allergen_id: int) -> QuerySet[Ingredient]:
        """Get ingredients containing a specific allergen."""
        return self.get_active_ingredients().filter(
            allergens__id=allergen_id
        ).distinct()
    
    def get_by_allergens(self, allergen_ids: List[int]) -> QuerySet[Ingredient]:
        """Get ingredients containing any of the specified allergens."""
        return self.get_active_ingredients().filter(
            allergens__id__in=allergen_ids
        ).distinct()
    
    @transaction.atomic
    def create_ingredient(self, data: Dict[str, Any]) -> Ingredient:
        """Create an ingredient with allergen associations."""
        allergens = data.pop('allergens', [])
        
        try:
            ingredient = super().create(**data)
            if allergens:
                ingredient.allergens.set(allergens)
            return ingredient
        except ValidationError as e:
            raise ValidationError(f"Error creating ingredient: {str(e)}")
    
    @transaction.atomic
    def update_ingredient(self, ingredient: Ingredient, data: Dict[str, Any]) -> Ingredient:
        """Update an ingredient with allergen associations."""
        allergens = data.pop('allergens', None)
        
        try:
            ingredient = super().update(ingredient, **data)
            if allergens is not None:
                ingredient.allergens.set(allergens)
            return ingredient
        except ValidationError as e:
            raise ValidationError(f"Error updating ingredient: {str(e)}")
    
    @transaction.atomic
    def toggle_active_status(self, ingredient: Ingredient) -> Ingredient:
        """Toggle ingredient active status with validation."""
        if ingredient.usage_count > 0 and ingredient.is_active:
            raise ValidationError(
                "Cannot deactivate ingredient that is currently used in products"
            )
        
        return self.update(ingredient, is_active=not ingredient.is_active)
    
    def search_ingredients(self, query: str) -> QuerySet[Ingredient]:
        """Search ingredients by name or description."""
        return self.get_active_ingredients().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    
    def get_ingredients_without_allergens(self) -> QuerySet[Ingredient]:
        """Get ingredients that don't have any allergens."""
        return self.get_active_ingredients().filter(allergens__isnull=True)
    
    def get_commonly_used_ingredients(self, limit: int = 10) -> QuerySet[Ingredient]:
        """Get most commonly used ingredients."""
        return self.get_active_ingredients().order_by('-usage_count')[:limit]
    
    def get_ingredient_statistics(self) -> Dict[str, Any]:
        """Get statistics about ingredients."""
        queryset = self.get_queryset()
        return {
            'total_ingredients': queryset.count(),
            'active_ingredients': queryset.filter(is_active=True).count(),
            'ingredients_with_allergens': queryset.filter(allergens__isnull=False).distinct().count(),
            'ingredients_without_allergens': queryset.filter(allergens__isnull=True).count(),
            'avg_allergens_per_ingredient': queryset.annotate(
                allergen_count=Count('allergens')
            ).aggregate(avg_allergens=models.Avg('allergen_count'))['avg_allergens'],
            'most_used_ingredients': list(
                self.get_commonly_used_ingredients(5).values('id', 'name', 'usage_count')
            )
        }
    
    @transaction.atomic
    def bulk_update_allergens(self, ingredient_allergens: List[Dict[str, Any]]) -> None:
        """Bulk update allergens for multiple ingredients."""
        with transaction.atomic():
            for item in ingredient_allergens:
                ingredient = self.get_by_id(item['ingredient_id'])
                if ingredient:
                    ingredient.allergens.set(item['allergen_ids'])
