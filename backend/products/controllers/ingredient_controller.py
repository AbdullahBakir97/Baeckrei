from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ..services.ingredient_service import IngredientService
from ..models import Ingredient

class IngredientController:
    """Controller class for handling ingredient-related business logic."""
    
    def __init__(self):
        self.service = IngredientService()
    
    def get_ingredient_list(self, filters: Dict[str, Any]) -> QuerySet[Ingredient]:
        """Get filtered list of ingredients."""
        # Start with active ingredients
        queryset = self.service.get_active_ingredients()
        
        # Apply search if provided
        search_query = filters.get('search')
        if search_query:
            queryset = self.service.search_ingredients(search_query)
        
        # Filter by allergen if provided
        allergen_ids = filters.get('allergens', [])
        if allergen_ids:
            queryset = self.service.get_by_allergens(allergen_ids)
        
        # Filter by no allergens if specified
        no_allergens = filters.get('no_allergens', False)
        if no_allergens:
            queryset = self.service.get_ingredients_without_allergens()
        
        return queryset.distinct()
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get ingredient by ID."""
        ingredient = self.service.get_by_id(ingredient_id)
        if not ingredient:
            raise ValidationError(f"Ingredient with ID {ingredient_id} not found")
        return ingredient
    
    def create_ingredient(self, data: Dict[str, Any]) -> Ingredient:
        """Create a new ingredient."""
        try:
            return self.service.create_ingredient(data)
        except ValidationError as e:
            raise ValidationError(f"Invalid ingredient data: {str(e)}")
    
    def update_ingredient(self, ingredient_id: int, data: Dict[str, Any]) -> Ingredient:
        """Update an existing ingredient."""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        try:
            return self.service.update_ingredient(ingredient, data)
        except ValidationError as e:
            raise ValidationError(f"Invalid ingredient data: {str(e)}")
    
    def delete_ingredient(self, ingredient_id: int) -> None:
        """Delete an ingredient."""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        try:
            self.service.delete(ingredient)
        except Exception as e:
            raise ValidationError(f"Error deleting ingredient: {str(e)}")
    
    def toggle_ingredient_status(self, ingredient_id: int) -> Ingredient:
        """Toggle ingredient active status."""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        try:
            return self.service.toggle_active_status(ingredient)
        except ValidationError as e:
            raise ValidationError(f"Error toggling ingredient status: {str(e)}")
    
    def get_commonly_used_ingredients(self, limit: int = 10) -> QuerySet[Ingredient]:
        """Get commonly used ingredients."""
        return self.service.get_commonly_used_ingredients(limit)
    
    def bulk_update_allergens(self, ingredient_allergens: List[Dict[str, Any]]) -> None:
        """Bulk update ingredient allergens."""
        try:
            self.service.bulk_update_allergens(ingredient_allergens)
        except Exception as e:
            raise ValidationError(f"Error updating ingredient allergens: {str(e)}")
    
    def get_ingredient_statistics(self) -> Dict[str, Any]:
        """Get ingredient statistics."""
        try:
            return self.service.get_ingredient_statistics()
        except Exception as e:
            raise ValidationError(f"Error generating ingredient statistics: {str(e)}")
