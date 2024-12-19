from typing import Dict, Any
from django.db.models import QuerySet
from ..services.ingredient_service import IngredientService
from ..models import Ingredient

class IngredientController:
    """Controller for handling ingredient-related operations."""
    
    def __init__(self):
        self.service = IngredientService()
    
    def get_ingredient_list(self, filters: Dict[str, Any]) -> QuerySet[Ingredient]:
        """Get filtered list of ingredients."""
        queryset = self.service.get_queryset()
        
        # Apply search if provided
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        # Apply allergen filter if provided
        allergen = filters.get('allergen')
        if allergen:
            queryset = queryset.filter(allergens__name__iexact=allergen)
        
        return queryset.distinct()
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        """Get ingredient by ID."""
        return self.service.get_by_id(ingredient_id)
    
    def create_ingredient(self, data: Dict[str, Any]) -> Ingredient:
        """Create a new ingredient."""
        return self.service.create(**data)
    
    def update_ingredient(self, ingredient: Ingredient, data: Dict[str, Any]) -> Ingredient:
        """Update an existing ingredient."""
        return self.service.update(ingredient, **data)
    
    def delete_ingredient(self, ingredient: Ingredient) -> None:
        """Delete an ingredient."""
        self.service.delete(ingredient)
