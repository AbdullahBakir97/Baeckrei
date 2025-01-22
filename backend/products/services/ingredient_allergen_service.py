from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet, Count, F, Q, Model
from django.db import transaction
from ..models import Ingredient, AllergenInfo
from .base import BaseService
from .. import EXCEPTIONS
import uuid

class IngredientAllergenService(BaseService[Ingredient]):
    """Service for managing ingredients and their allergens together."""

    def __init__(self):
        super().__init__(Ingredient)

    def get_by_id(self, model_id: Union[uuid.UUID, str], model_class: Model = None) -> Optional[Union[Ingredient, AllergenInfo]]:
        """Get an ingredient or allergen by ID."""
        try:
            if model_class is None:
                model_class = self.model
            return model_class.objects.get(id=model_id)
        except model_class.DoesNotExist:
            return None

    def get_allergen_by_id(self, allergen_id: Union[uuid.UUID, str]) -> Optional[AllergenInfo]:
        """Get allergen by ID with usage counts."""
        try:
            return self.get_by_id(allergen_id, AllergenInfo).with_counts().get(id=allergen_id)
        except AllergenInfo.DoesNotExist:
            return None

    def get_ingredient_by_id(self, ingredient_id: Union[uuid.UUID, str]) -> Optional[Ingredient]:
        """Get ingredient by ID with related data."""
        return self.get_by_id(ingredient_id)

    def get_by_name(self, name: str, model_class) -> Optional[Union[Ingredient, AllergenInfo]]:
        """Get ingredient or allergen by exact name match."""
        return model_class.objects.filter(name__iexact=name).first()

    @transaction.atomic
    def create_ingredient_with_allergens(self, data: Dict[str, Any]) -> Ingredient:
        """Create an ingredient with its allergens."""
        try:
            # Validate required fields
            if 'name' not in data:
                raise EXCEPTIONS.ValidationError(
                    field='name',
                    reason='Missing required field',
                    message="Ingredient name is required"
                )

            # Check for duplicate name
            if self.get_by_name(data['name'], Ingredient):
                raise EXCEPTIONS.DuplicateIngredientError(
                    name=data['name'],
                    message=f"Ingredient with name '{data['name']}' already exists"
                )

            # Extract allergens
            allergen_ids = data.pop('allergens', [])
            
            # Set default active status
            data.setdefault('is_active', True)
            
            # Create ingredient
            ingredient = super().create(**data)
            
            # Add allergens if provided
            if allergen_ids:
                self.set_ingredient_allergens(ingredient.id, allergen_ids)
            
            return ingredient
            
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.DuplicateIngredientError):
            raise
        except Exception as e:
            raise EXCEPTIONS.IngredientError(
                message=f"Error creating ingredient: {str(e)}",
                code="INGREDIENT_CREATE_ERROR"
            )

    @transaction.atomic
    def update_ingredient_with_allergens(self, ingredient_id: uuid.UUID, data: Dict[str, Any]) -> Ingredient:
        """Update an ingredient and its allergens."""
        try:
            ingredient = self.get_by_id(ingredient_id)
            if not ingredient:
                raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
            
            # Check for duplicate name if name is being changed
            name = data.get('name')
            if name and name != ingredient.name:
                if self.get_by_name(name, Ingredient):
                    raise EXCEPTIONS.DuplicateIngredientError(
                        name=name,
                        message=f"Another ingredient with name '{name}' already exists"
                    )
            
            # Handle allergens separately
            allergen_ids = data.pop('allergens', None)
            
            # Update ingredient
            ingredient = super().update(ingredient, **data)
            
            # Update allergens if provided
            if allergen_ids is not None:
                self.set_ingredient_allergens(ingredient_id, allergen_ids)
            
            return ingredient
            
        except (EXCEPTIONS.IngredientNotFoundError, EXCEPTIONS.DuplicateIngredientError):
            raise
        except Exception as e:
            raise EXCEPTIONS.IngredientError(
                message=f"Error updating ingredient: {str(e)}",
                code="INGREDIENT_UPDATE_ERROR"
            )

    @transaction.atomic
    def merge_ingredients(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Ingredient:
        """Merge source ingredient into target ingredient."""
        source = self.get_by_id(source_id)
        target = self.get_by_id(target_id)
        
        if not source or not target:
            raise EXCEPTIONS.IngredientNotFoundError(
                ingredient_id=source_id if not source else target_id
            )
        
        if source.id == target.id:
            raise EXCEPTIONS.ValidationError(
                field='ingredient_ids',
                reason='Cannot merge an ingredient with itself'
            )
        
        try:
            return target.merge_with(source)
        except Exception as e:
            raise EXCEPTIONS.IngredientError(
                message=f"Error merging ingredients: {str(e)}",
                code="INGREDIENT_MERGE_ERROR"
            )

    @transaction.atomic
    def merge_allergens(self, source_id: uuid.UUID, target_id: uuid.UUID) -> AllergenInfo:
        """Merge source allergen into target allergen."""
        source = self.get_allergen_by_id(source_id)
        target = self.get_allergen_by_id(target_id)
        
        if not source or not target:
            raise EXCEPTIONS.AllergenNotFoundError(
                allergen_id=source_id if not source else target_id
            )
            
        if source.id == target.id:
            raise EXCEPTIONS.ValidationError(
                field='allergen_ids',
                reason='Cannot merge an allergen with itself'
            )
            
        try:
            return target.merge_with(source)
        except Exception as e:
            raise EXCEPTIONS.AllergenError(
                message=f"Error merging allergens: {str(e)}",
                code="ALLERGEN_MERGE_ERROR"
            )

    def toggle_ingredient_status(self, ingredient_id: uuid.UUID) -> Ingredient:
        """Toggle ingredient active status."""
        ingredient = self.get_by_id(ingredient_id)
        if not ingredient:
            raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
        
        try:
            return ingredient.toggle_status()
        except EXCEPTIONS.IngredientInUseError:
            raise
        except Exception as e:
            raise EXCEPTIONS.IngredientError(
                message=f"Error toggling ingredient status: {str(e)}",
                code="INGREDIENT_STATUS_ERROR"
            )

    @transaction.atomic
    def create_allergen(self, data: Dict[str, Any]) -> AllergenInfo:
        """Create a new allergen with validation."""
        try:
            if 'name' not in data:
                raise EXCEPTIONS.ValidationError(
                    field='name',
                    reason='Missing required field',
                    message="Allergen name is required"
                )
                
            # Check for duplicate name
            if self.get_by_name(data['name'], AllergenInfo):
                raise EXCEPTIONS.DuplicateAllergenError(
                    name=data['name']
                )
                
            return AllergenInfo.objects.create(**data)
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.DuplicateAllergenError):
            raise
        except Exception as e:
            raise EXCEPTIONS.AllergenError(
                message=f"Error creating allergen: {str(e)}",
                code="ALLERGEN_CREATE_ERROR"
            )

    @transaction.atomic
    def update_allergen(self, allergen_id: uuid.UUID, data: Dict[str, Any]) -> AllergenInfo:
        """Update an allergen with validation."""
        allergen = self.get_allergen_by_id(allergen_id)
        if not allergen:
            raise EXCEPTIONS.AllergenNotFoundError(allergen_id=allergen_id)
            
        # Check for duplicate name if being changed
        name = data.get('name')
        if name and name != allergen.name:
            if self.get_by_name(name, AllergenInfo):
                raise EXCEPTIONS.DuplicateAllergenError(name=name)
                
        try:
            for key, value in data.items():
                setattr(allergen, key, value)
            allergen.save()
            return allergen
        except Exception as e:
            raise EXCEPTIONS.AllergenError(
                message=f"Error updating allergen: {str(e)}",
                code="ALLERGEN_UPDATE_ERROR"
            )

    @transaction.atomic
    def set_ingredient_allergens(self, ingredient_id: uuid.UUID, allergen_ids: List[uuid.UUID]) -> None:
        """Set allergens for an ingredient."""
        ingredient = self.get_by_id(ingredient_id)
        if not ingredient:
            raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
            
        try:
            ingredient.set_allergens(allergen_ids)
        except EXCEPTIONS.AllergenNotFoundError:
            raise
        except Exception as e:
            raise EXCEPTIONS.IngredientError(
                message=f"Error setting ingredient allergens: {str(e)}",
                code="INGREDIENT_ALLERGEN_ERROR"
            )

    @transaction.atomic
    def delete_allergen(self, allergen_id: uuid.UUID) -> None:
        """Delete an allergen if not in use."""
        allergen = self.get_allergen_by_id(allergen_id)
        if not allergen:
            raise EXCEPTIONS.AllergenNotFoundError(
                allergen_id=allergen_id,
                message=f"Cannot delete allergen: Allergen with ID '{allergen_id}' not found"
            )
            
        try:
            allergen.delete()
        except EXCEPTIONS.AllergenInUseError:
            raise
        except Exception as e:
            raise EXCEPTIONS.AllergenError(
                message=f"Error deleting allergen: {str(e)}",
                code="ALLERGEN_DELETE_ERROR"
            )

    def get_ingredients_by_allergen(self, allergen_id: uuid.UUID) -> QuerySet[Ingredient]:
        """Get ingredients containing a specific allergen."""
        return self.ingredients.by_allergen(allergen_id)

    def get_allergen_statistics(self) -> Dict[str, Any]:
        """Get comprehensive allergen statistics."""
        return self.allergens.get_statistics()

    def get_ingredient_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ingredient statistics."""
        return self.ingredients.get_statistics()

    def get_allergens_for_ingredients(self, ingredient_ids: List[uuid.UUID]) -> QuerySet[AllergenInfo]:
        """Get all allergens associated with a list of ingredients."""
        return self.allergens.for_ingredients(ingredient_ids)

    def get_category_allergens(self, category_id: uuid.UUID) -> QuerySet[AllergenInfo]:
        """Get all allergens associated with products in a category."""
        return self.allergens.in_category(category_id)

    def get_product_allergens(self, product_id: uuid.UUID) -> QuerySet[AllergenInfo]:
        """Get all allergens associated with a product through its ingredients."""
        product = self.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)
        
        ingredient_ids = [ingredient.id for ingredient in product.ingredients.all()]
        return self.get_allergens_for_ingredients(ingredient_ids)

    def get_allergens_in_category(self, category_id: uuid.UUID) -> QuerySet[AllergenInfo]:
        """Get all allergens associated with products in a category with usage stats."""
        return self.allergens.with_counts().in_category(category_id)
