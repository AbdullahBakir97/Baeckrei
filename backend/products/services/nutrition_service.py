from typing import Optional, Dict, Any, Union, List
from django.db.models import QuerySet
from django.db import transaction
from decimal import Decimal
from ..models import NutritionInfo
from .base import BaseService
from .. import EXCEPTIONS
import uuid

class NutritionService(BaseService[NutritionInfo]):
    """Service class for managing nutrition information."""

    def __init__(self):
        super().__init__(NutritionInfo)

    @transaction.atomic
    def create_nutrition_info(self, data: Dict[str, Any]) -> NutritionInfo:
        """Create new nutrition information."""
        try:
            NutritionInfo.validate_nutrition_data(data)
            return super().create(**data)
        except EXCEPTIONS.NutritionValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.NutritionError(
                message=f"Error creating nutrition info: {str(e)}",
                code="NUTRITION_CREATE_ERROR"
            )

    @transaction.atomic
    def update_nutrition_info(self, nutrition_id: Union[str, uuid.UUID], data: Dict[str, Any]) -> NutritionInfo:
        """Update existing nutrition information."""
        nutrition_info = self.get_by_id(nutrition_id)
        if not nutrition_info:
            raise EXCEPTIONS.NutritionNotFoundError(nutrition_id=nutrition_id)

        try:
            NutritionInfo.validate_nutrition_data(data)
            return super().update(nutrition_info, **data)
        except EXCEPTIONS.NutritionValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.NutritionError(
                message=f"Error updating nutrition info: {str(e)}",
                code="NUTRITION_UPDATE_ERROR"
            )

    def get_nutrition_info(self, nutrition_id: Union[str, uuid.UUID]) -> Optional[NutritionInfo]:
        """Get nutrition information by ID."""
        nutrition_info = self.get_by_id(nutrition_id)
        if not nutrition_info:
            raise EXCEPTIONS.NutritionNotFoundError(nutrition_id=nutrition_id)
        return nutrition_info

    @transaction.atomic
    def delete_nutrition_info(self, nutrition_id: Union[str, uuid.UUID]) -> None:
        """Delete nutrition information."""
        nutrition_info = self.get_by_id(nutrition_id)
        if not nutrition_info:
            raise EXCEPTIONS.NutritionNotFoundError(nutrition_id=nutrition_id)

        try:
            super().delete(nutrition_info)
        except Exception as e:
            raise EXCEPTIONS.NutritionError(
                message=f"Error deleting nutrition info: {str(e)}",
                code="NUTRITION_DELETE_ERROR"
            )

    def get_nutrition_stats(self, category_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get nutrition statistics for a category."""
        return NutritionInfo.objects.get_statistics(category_id)

    def get_nutrition_distribution(self, nutrient: str, category_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get distribution of values for a specific nutrient."""
        return NutritionInfo.objects.get_distribution(nutrient, category_id)

    def find_similar_products(
        self,
        nutrition_id: uuid.UUID,
        diet_preferences: Optional[Dict[str, Any]] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find products with similar nutritional values."""
        nutrition_info = self.get_by_id(nutrition_id)
        if not nutrition_info:
            raise EXCEPTIONS.NutritionNotFoundError(nutrition_id=nutrition_id)

        return NutritionInfo.objects.find_similar(
            nutrition_info.to_dict(),
            max_results=max_results,
            diet_preferences=diet_preferences
        )

    def get_comprehensive_info(
        self,
        nutrition_id: uuid.UUID,
        weight_grams: Optional[Decimal] = None,
        diet_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive nutrition information.
        
        Args:
            nutrition_id: ID of the nutrition info to get
            weight_grams: Optional specific weight to calculate for
            diet_type: Optional diet type for daily value calculation
            
        Returns:
            Dictionary containing:
            - nutrition_values: Base nutrition values
            - daily_percentages: Percentage of daily values if diet_type provided
            - weight_based: Nutrition for specific weight if provided
        """
        nutrition_info = self.get_by_id(nutrition_id)
        if not nutrition_info:
            raise EXCEPTIONS.NutritionNotFoundError(nutrition_id=nutrition_id)

        result = {
            'nutrition_values': nutrition_info.to_dict(),
            'per_weight': 100  # Base values are per 100g
        }

        # Add daily value percentages if requested
        if diet_type:
            result['daily_percentages'] = NutritionInfo.objects.calculate_daily_percentages(
                nutrition_info=nutrition_info,
                weight_grams=weight_grams or Decimal('100'),
                diet_type=diet_type
            )

        # Add weight-based values if requested
        if weight_grams:
            result['weight_based'] = {
                'weight_grams': weight_grams,
                'values': nutrition_info.convert_to_weight(weight_grams)
            }

        return result

    def get_queryset(self) -> QuerySet[NutritionInfo]:
        """Get the base queryset with related product."""
        return super().get_queryset().select_related('product')
