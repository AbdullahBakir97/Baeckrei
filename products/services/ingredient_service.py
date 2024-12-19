from django.db.models import QuerySet
from ..models import Ingredient
from .base import BaseService

class IngredientService(BaseService[Ingredient]):
    """Service for handling ingredient-related operations."""
    
    def __init__(self):
        super().__init__(Ingredient)
    
    def get_queryset(self) -> QuerySet[Ingredient]:
        """Get base queryset with related fields."""
        return super().get_queryset().prefetch_related('allergens')
    
    def get_active_ingredients(self) -> QuerySet[Ingredient]:
        """Get all active ingredients."""
        return self.get_queryset().filter(is_active=True)
    
    def get_by_allergen(self, allergen_name: str) -> QuerySet[Ingredient]:
        """Get ingredients containing a specific allergen."""
        return self.get_queryset().filter(
            allergens__name__iexact=allergen_name
        ).distinct()
    
    def toggle_active_status(self, ingredient: Ingredient) -> Ingredient:
        """Toggle ingredient active status."""
        ingredient.is_active = not ingredient.is_active
        ingredient.save()
        return ingredient
