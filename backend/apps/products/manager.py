from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import uuid
import statistics
from django.db import models
from django.db.models import Q, Avg, Min, Max, Count, F, Sum
from .querysets import IngredientQuerySet, NutritionQuerySet, CategoryQuerySet, ProductQuerySet, AllergenQuerySet

class IngredientManager(models.Manager):
    def get_queryset(self):
        return IngredientQuerySet(self.model, using=self._db)

    def with_related(self):
        """Get queryset with related data."""
        return self.get_queryset().with_related()

    def with_product_stats(self):
        """Get queryset with product-related statistics."""
        return self.get_queryset().with_product_stats()

    def get_active(self):
        """Get all active ingredients."""
        return self.get_queryset().with_related().active()

    def search(self, query: str):
        """Search active ingredients."""
        return self.get_queryset().search(query)

    def by_allergen(self, allergen_id: uuid.UUID):
        """Get ingredients with specific allergen."""
        return self.get_queryset().with_related().by_allergen(allergen_id)

    def get_allergens_for_ingredients(self, ingredient_ids: List[uuid.UUID]):
        """Get all allergens for a list of ingredient IDs."""
        return self.get_queryset().get_allergens_for_ingredients(ingredient_ids)

    def get_ingredients_by_allergen(self, allergen_id: uuid.UUID):
        """Get ingredients containing a specific allergen."""
        return self.get_queryset().get_ingredients_by_allergen(allergen_id)

    def get_ingredient_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ingredient statistics."""
        return self.get_queryset().get_ingredient_statistics()

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ingredient statistics."""
        qs = self.with_related()
        return {
            'total': qs.count(),
            'active': qs.active().count(),
            'with_allergens': qs.with_allergens().count(),
            'without_allergens': qs.without_allergens().count(),
            'most_used': list(qs.most_used().values('id', 'name', 'usage_count'))
        }



class AllergenManager(models.Manager):
    def get_queryset(self):
        return AllergenQuerySet(self.model, using=self._db)

    def with_counts(self):
        """Get queryset with counts."""
        return self.get_queryset().with_counts()

    def get_unused(self):
        """Get unused allergens."""
        return self.get_queryset().unused()

    def in_use(self):
        return self.get_queryset().in_use()

    def get_most_common(self, limit: int = 10):
        """Get most common allergens."""
        return self.get_queryset().most_common(limit)

    def in_category(self, category_id: uuid.UUID):
        """Get allergens in category."""
        return self.get_queryset().in_category(category_id)

    def search(self, query: str):
        """Search allergens."""
        return self.get_queryset().search(query)

    def for_ingredients(self, ingredient_ids: List[uuid.UUID]):
        """Get allergens for ingredients."""
        return self.get_queryset().for_ingredients(ingredient_ids)

    def get_allergens_in_category(self, category_id: uuid.UUID):
        """Get allergens used in a category."""
        return self.get_queryset().get_allergens_in_category(category_id)

    def get_allergen_statistics(self) -> Dict[str, Any]:
        """Get comprehensive allergen statistics."""
        return self.get_queryset().get_allergen_statistics()

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive allergen statistics."""
        qs = self.with_counts()
        return {
            'total': qs.count(),
            'in_use': qs.in_use().count(),
            'unused': qs.unused().count(),
            'most_common': list(qs.most_common().values(
                'id', 'name', 'ingredient_count', 'product_count'
            ))
        }



class ProductManager(models.Manager):
    """Manager class for Product model with enhanced querying capabilities."""

    def get_queryset(self):
        """Get the custom queryset."""
        return ProductQuerySet(self.model, using=self._db)

    def with_related(self):
        """Get queryset with related fields."""
        return self.get_queryset().with_related()

    def filter_products(self, 
                       filters: Dict[str, Any] = None,
                       search_query: Optional[str] = None,
                       ordering: Optional[List[str]] = None):
        """
        High-level method to filter products using the filtering system.
        
        This provides a clean interface to the filtering system while
        maintaining the chainable nature of querysets.
        """
        return self.get_queryset().apply_filters(
            filters=filters,
            search_query=search_query,
            ordering=ordering
        )

    def available(self):
        """Get all available products."""
        return self.get_queryset().available()

    def by_category(self, category_ids: Optional[List[uuid.UUID]] = None):
        """Get products by category IDs."""
        return self.get_queryset().by_category(category_ids)

    def by_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        """Get products within price range."""
        return self.get_queryset().by_price_range(min_price, max_price)

    def by_ingredient(self, ingredient_id: uuid.UUID):
        """Get products containing a specific ingredient."""
        return self.get_queryset().by_ingredient(ingredient_id)

    def search(self, query: str):
        """Search products."""
        return self.get_queryset().search(query)

    def featured(self, limit: int = 6):
        """Get featured products."""
        return self.get_queryset().featured(limit)

    def dietary_preferences(self, **preferences):
        """Get products filtered by dietary preferences."""
        return self.get_queryset().dietary_preferences(**preferences)

    def related_products(self, product_id: uuid.UUID, limit: int = 4):
        """Get related products for a given product ID."""
        return self.get_queryset().related_products(product_id, limit)



class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def with_product_stats(self):
        """Get queryset with product-related statistics."""
        return self.get_queryset().with_product_stats()

    def filter_categories(self,
                        filters: Dict[str, Any] = None,
                        search_query: Optional[str] = None,
                        ordering: Optional[List[str]] = None):
        """
        High-level method to filter categories using the filtering system.
        
        This provides a clean interface to the filtering system while
        maintaining the chainable nature of querysets.
        """
        return self.get_queryset().apply_filters(
            filters=filters,
            search_query=search_query,
            ordering=ordering
        )

    def with_counts(self):
        """Get queryset with counts."""
        return self.get_queryset().with_counts()

    def get_active(self):
        """Get active categories with products."""
        return self.get_queryset().with_counts().active().with_products()

    def by_slug(self, slug: str):
        """Get category by slug."""
        return self.get_queryset().with_counts().by_slug(slug)

    def search(self, query: str):
        """Search categories."""
        return self.get_queryset().search(query)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive category statistics."""
        qs = self.with_counts()
        return {
            'total_categories': qs.count(),
            'active_categories': qs.active().count(),
            'categories_with_products': qs.with_products().count(),
            'avg_products_per_category': qs.aggregate(
                avg_products=Count('products')
            )['avg_products']
        }



class NutritionManager(models.Manager):
    # Predefined diet types with their daily values
    DIET_TYPES = {
        'standard': {  # FDA 2000 calorie diet
            'proteins': Decimal('50'),
            'carbohydrates': Decimal('275'),
            'fats': Decimal('78'),
            'fiber': Decimal('28'),
            'calories': Decimal('2000')
        },
        'keto': {
            'proteins': Decimal('75'),
            'carbohydrates': Decimal('50'),
            'fats': Decimal('165'),
            'fiber': Decimal('28'),
            'calories': Decimal('2000')
        },
        'low_carb': {
            'proteins': Decimal('75'),
            'carbohydrates': Decimal('125'),
            'fats': Decimal('111'),
            'fiber': Decimal('28'),
            'calories': Decimal('2000')
        },
        'high_protein': {
            'proteins': Decimal('150'),
            'carbohydrates': Decimal('275'),
            'fats': Decimal('67'),
            'fiber': Decimal('28'),
            'calories': Decimal('2500')
        },
        'mediterranean': {
            'proteins': Decimal('75'),
            'carbohydrates': Decimal('275'),
            'fats': Decimal('89'),
            'fiber': Decimal('35'),
            'calories': Decimal('2200')
        }
    }

    def get_queryset(self):
        return NutritionQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()

    def by_category(self, category_id: Optional[uuid.UUID] = None):
        return self.get_queryset().by_category(category_id)

    def get_statistics(self, category_id: Optional[uuid.UUID] = None):
        """Get comprehensive nutrition statistics."""
        qs = self.by_category(category_id)
        stats = qs.with_stats()
        
        # Calculate percentiles and standard deviation
        nutrients = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']
        result = {}

        for nutrient in nutrients:
            values = list(qs.values_list(nutrient, flat=True))
            if not values:
                continue

            # Calculate percentiles
            sorted_values = sorted(values)
            length = len(sorted_values)
            percentiles = {
                'p25': sorted_values[int(length * 0.25)],
                'p50': sorted_values[int(length * 0.50)],
                'p75': sorted_values[int(length * 0.75)]
            }

            # Map the field name for carbohydrates in stats
            stat_field = 'carbs' if nutrient == 'carbohydrates' else nutrient
            
            result[nutrient] = {
                'avg': stats[f'avg_{stat_field}'],
                'min': stats[f'min_{stat_field}'],
                'max': stats[f'max_{stat_field}'],
                'percentiles': percentiles,
                'std_dev': Decimal(str(statistics.stdev(values))) if len(values) > 1 else Decimal('0')
            }

        return result

    def find_similar(self, 
                    nutrition_values: Dict[str, Decimal],
                    tolerance: Decimal = Decimal('0.2'),
                    max_results: int = 10,
                    diet_preferences: Optional[Dict[str, Any]] = None):
        """Find products with similar nutrition values."""
        qs = self.get_queryset()
        
        if diet_preferences:
            qs = qs.with_dietary_restrictions(**diet_preferences)
            
        return qs.similar_to(
            nutrition_values,
            tolerance=tolerance
        ).with_related()[:max_results]

    def get_distribution(self,
                        nutrient: str,
                        category_id: Optional[uuid.UUID] = None,
                        bins: int = 10):
        """Get distribution of values for a specific nutrient."""
        if nutrient not in ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']:
            raise ValueError(f"Invalid nutrient name: {nutrient}")

        values = list(self.by_category(category_id).values_list(nutrient, flat=True))
        if not values:
            return {'bins': [], 'counts': [], 'percentages': []}

        counts, bin_edges = numpy.histogram(values, bins=bins)
        total_count = sum(counts)
        
        return {
            'bins': [round(float(edge), 2) for edge in bin_edges],
            'counts': [int(count) for count in counts],
            'percentages': [round(float(count/total_count * 100), 2) for count in counts]
        }

    def get_daily_values(self, diet_type: Optional[str] = None) -> Dict[str, Decimal]:
        """Get daily recommended values for a specific diet type."""
        if not diet_type or diet_type.lower() not in self.DIET_TYPES:
            return self.DIET_TYPES['standard']
        return self.DIET_TYPES[diet_type.lower()]

    def calculate_daily_percentages(
        self,
        nutrition_info,
        weight_grams: Decimal,
        custom_daily_values: Optional[Dict[str, Decimal]] = None,
        diet_type: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """Calculate percentage of daily recommended values."""
        # Get daily values based on diet type or custom values
        daily_values = custom_daily_values or self.get_daily_values(diet_type)
        
        # Calculate actual nutrition values for the given weight
        actual_values = nutrition_info.calculate_for_weight(
            weight_grams=weight_grams,
            custom_fields=list(daily_values.keys())
        )
        
        # Calculate percentages for each nutrient
        result = {}
        for nutrient, daily_value in daily_values.items():
            if daily_value > 0:
                percentage = (actual_values[nutrient] / daily_value) * 100
                result[nutrient] = round(percentage, 1)
            else:
                result[nutrient] = Decimal('0.0')
                
        return result