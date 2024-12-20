from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ..services.allergen_service import AllergenService
from ..models import AllergenInfo

class AllergenController:
    """Controller class for handling allergen-related business logic."""
    
    def __init__(self):
        self.service = AllergenService()
    
    def get_allergen_list(self, filters: Dict[str, Any]) -> QuerySet[AllergenInfo]:
        """Get filtered list of allergens."""
        queryset = self.service.get_queryset()
        
        # Apply search if provided
        search_query = filters.get('search')
        if search_query:
            queryset = self.service.search_allergens(search_query)
        
        # Filter by usage if specified
        in_use = filters.get('in_use')
        if in_use is not None:
            if in_use:
                queryset = queryset.filter(ingredient_count__gt=0)
            else:
                queryset = self.service.get_unused_allergens()
        
        return queryset.distinct()
    
    def get_allergen_by_id(self, allergen_id: int) -> Optional[AllergenInfo]:
        """Get allergen by ID."""
        allergen = self.service.get_by_id(allergen_id)
        if not allergen:
            raise ValidationError(f"Allergen with ID {allergen_id} not found")
        return allergen
    
    def get_allergen_by_name(self, name: str) -> Optional[AllergenInfo]:
        """Get allergen by name."""
        allergen = self.service.get_by_name(name)
        if not allergen:
            raise ValidationError(f"Allergen with name '{name}' not found")
        return allergen
    
    def create_allergen(self, data: Dict[str, Any]) -> AllergenInfo:
        """Create a new allergen."""
        try:
            return self.service.create_allergen(data)
        except ValidationError as e:
            raise ValidationError(f"Invalid allergen data: {str(e)}")
    
    def update_allergen(self, allergen_id: int, data: Dict[str, Any]) -> AllergenInfo:
        """Update an existing allergen."""
        allergen = self.get_allergen_by_id(allergen_id)
        try:
            return self.service.update_allergen(allergen, data)
        except ValidationError as e:
            raise ValidationError(f"Invalid allergen data: {str(e)}")
    
    def delete_allergen(self, allergen_id: int) -> None:
        """Delete an allergen."""
        allergen = self.get_allergen_by_id(allergen_id)
        try:
            self.service.delete(allergen)
        except Exception as e:
            raise ValidationError(f"Error deleting allergen: {str(e)}")
    
    def get_most_common_allergens(self, limit: int = 10) -> QuerySet[AllergenInfo]:
        """Get most common allergens."""
        return self.service.get_most_common_allergens(limit)
    
    def get_allergens_by_category(self, category_id: int) -> QuerySet[AllergenInfo]:
        """Get allergens used in a specific category."""
        return self.service.get_allergens_in_category(category_id)
    
    def merge_allergens(self, source_id: int, target_id: int) -> AllergenInfo:
        """Merge one allergen into another."""
        try:
            return self.service.merge_allergens(source_id, target_id)
        except ValidationError as e:
            raise ValidationError(f"Error merging allergens: {str(e)}")
    
    def get_allergen_statistics(self) -> Dict[str, Any]:
        """Get allergen statistics."""
        try:
            return self.service.get_allergen_statistics()
        except Exception as e:
            raise ValidationError(f"Error generating allergen statistics: {str(e)}")
