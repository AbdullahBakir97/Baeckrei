from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import uuid
import statistics
from django.db import models
from django.db.models import Q, Avg, Min, Max, Count, F, Sum

class IngredientQuerySet(models.QuerySet):
    def with_related(self):
        """Get queryset with related allergens and usage counts."""
        return self.prefetch_related(
            'allergens', 'products'
        ).annotate(
            usage_count=Count('products', distinct=True)
        )

    def with_product_stats(self):
        """Get queryset with product-related statistics."""
        return self.annotate(
            total_products=Count('products', distinct=True),
            affected_products=Count(
                'products',
                filter=Q(products__stock__lt=F('products__min_stock')),
                distinct=True
            ),
            out_of_stock_products=Count(
                'products',
                filter=Q(products__stock=0),
                distinct=True
            ),
            total_stock_value=Sum(
                F('products__stock') * F('products__price'),
                filter=Q(products__stock__gt=0)
            )
        )

    def active(self):
        """Get active ingredients."""
        return self.filter(is_active=True)

    def search(self, query: str):
        """Search ingredients by name, description, or allergen."""
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(allergens__name__icontains=query)
        ).distinct()

    def most_used(self, limit: int = 5):
        """Get most used ingredients."""
        return self.order_by('-usage_count')[:limit]

    def by_allergen(self, allergen_id: uuid.UUID):
        """Get ingredients containing a specific allergen."""
        return self.filter(allergens__id=allergen_id)

    def get_allergens_for_ingredients(self, ingredient_ids: List[uuid.UUID]):
        """Get all allergens for a list of ingredient IDs."""
        return (
            self.filter(id__in=ingredient_ids)
            .prefetch_related('allergens')
            .values_list('allergens', flat=True)
            .distinct()
        )

    def get_ingredients_by_allergen(self, allergen_id: uuid.UUID):
        """Get ingredients containing a specific allergen."""
        return self.filter(allergens__id=allergen_id).distinct()

    def get_ingredient_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ingredient statistics."""
        queryset = self.with_related()
        return {
            'total_count': queryset.count(),
            'active_count': queryset.filter(is_active=True).count(),
            'with_allergens': queryset.filter(allergens__isnull=False).distinct().count(),
            'without_allergens': queryset.filter(allergens__isnull=True).count(),
            'most_used': list(queryset.order_by('-usage_count')[:5].values(
                'id', 'name', 'usage_count'
            ))
        }

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

class AllergenQuerySet(models.QuerySet):
    def with_counts(self):
        """Add ingredient and product counts."""
        return self.annotate(
            ingredient_count=Count('ingredients', distinct=True),
            product_count=Count('ingredients__products', distinct=True)
        )

    def in_use(self):
        """Get allergens in use."""
        return self.with_counts().filter(ingredient_count__gt=0)

    def unused(self):
        """Get allergens not used in any ingredients."""
        return self.annotate(
            ingredient_count=Count('ingredients')
        ).filter(ingredient_count=0)

    def most_common(self, limit: int = 10):
        """Get most commonly used allergens."""
        return self.with_counts().order_by('-product_count')[:limit]

    def in_category(self, category_id: uuid.UUID):
        """Get allergens used in a category."""
        return self.filter(
            ingredients__products__category_id=category_id
        ).distinct()

    def search(self, query: str):
        """Search allergens by name or description."""
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    def for_ingredients(self, ingredient_ids: List[uuid.UUID]):
        """Get allergens for specific ingredients."""
        return self.filter(ingredients__id__in=ingredient_ids).distinct()

    def get_allergens_in_category(self, category_id: uuid.UUID):
        """Get allergens used in a category."""
        return (
            self.filter(ingredients__products__category_id=category_id)
            .distinct()
            .prefetch_related('ingredients')
        )

    def get_allergen_statistics(self) -> Dict[str, Any]:
        """Get comprehensive allergen statistics."""
        queryset = self.with_counts()
        return {
            'total_count': queryset.count(),
            'in_use_count': queryset.filter(ingredients__isnull=False).distinct().count(),
            'unused_count': queryset.filter(ingredients__isnull=True).count(),
            'most_common': list(queryset.order_by('-product_count')[:5].values(
                'id', 'name', 'ingredient_count', 'product_count'
            ))
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

class ProductQuerySet(models.QuerySet):
    """QuerySet class for Product model with optimized query methods."""

    def with_related(self):
        """Load all related fields for better performance."""
        return self.select_related(
            'category',
            'nutrition_info'
        ).prefetch_related(
            'ingredients',
            'ingredients__allergens'
        )

    def apply_filters(self, filters: Dict[str, Any] = None, 
                     search_query: Optional[str] = None,
                     ordering: Optional[List[str]] = None):
        """
        Apply filters, search, and ordering using ProductFilter.
        
        This method provides a clean interface to the filtering system
        while maintaining the chainable nature of querysets.
        """
        from products.filters import ProductFilter
        product_filter = ProductFilter(self)
        queryset = self

        if filters:
            queryset = product_filter.apply_filters(filters)
        
        if search_query:
            queryset = product_filter.apply_search(search_query)
            
        if ordering:
            queryset = product_filter.apply_ordering(ordering)
            
        return queryset

    def available(self):
        """Filter available products."""
        return self.filter(
            available=True,
            status='active',
            stock__gt=0
        )

    def by_category(self, category_ids: Optional[List[uuid.UUID]] = None):
        """Filter products by category IDs."""
        if not category_ids:
            return self
        return self.filter(category_id__in=category_ids)

    def by_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        """Filter products by price range."""
        queryset = self
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    def by_ingredient(self, ingredient_names: List[str]):
        """Filter products containing specific ingredients."""
        if not ingredient_names:
            return self
        return self.filter(ingredients__name__in=ingredient_names).distinct()

    def by_ingredient(self, ingredient_id: uuid.UUID):
        """Get products containing a specific ingredient."""
        return self.filter(ingredients__id=ingredient_id).distinct()

    def by_allergen(self, exclude_allergens: List[uuid.UUID]):
        """Exclude products containing specific allergens."""
        if not exclude_allergens:
            return self
        return self.exclude(
            ingredients__allergens__id__in=exclude_allergens
        ).distinct()

    def featured(self, limit: int = 6):
        """Get featured products."""
        return self.available().order_by('-created_at')[:limit]

    def dietary_preferences(self, vegan: bool = False, vegetarian: bool = False, gluten_free: bool = False):
        """Filter products by dietary preferences."""
        queryset = self.available()
        filters = {}
        if vegan:
            filters['is_vegan'] = True
        if vegetarian:
            filters['is_vegetarian'] = True
        if gluten_free:
            filters['is_gluten_free'] = True
        return queryset.filter(**filters) if filters else queryset

    def search(self, query: str):
        """Search products by name, description, or category."""
        if not query:
            return self
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    def with_stock_status(self):
        """Annotate products with stock status."""
        return self.annotate(
            is_low_stock=Q(stock__lte=F('min_stock_threshold')),
            needs_restock=Q(stock=0)
        )

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


class CategoryQuerySet(models.QuerySet):
    """QuerySet class for Category model with optimized query methods."""

    def with_product_stats(self):
        """Get queryset with product-related statistics."""
        return self.annotate(
            total_products=Count('products', distinct=True),
            active_products=Count(
                'products',
                filter=Q(products__available=True),
                distinct=True
            ),
            total_stock=Sum('products__stock'),
            total_value=Sum(
                F('products__stock') * F('products__price'),
                filter=Q(products__stock__gt=0)
            ),
            low_stock_count=Count(
                'products',
                filter=Q(products__stock__gt=0) & Q(products__stock__lt=F('products__min_stock')),
                distinct=True
            ),
            out_of_stock_count=Count(
                'products',
                filter=Q(products__stock=0),
                distinct=True
            )
        )

    def apply_filters(self, filters: Dict[str, Any] = None,
                     search_query: Optional[str] = None,
                     ordering: Optional[List[str]] = None):
        """
        Apply filters, search, and ordering using CategoryFilter.
        
        This method provides a clean interface to the filtering system
        while maintaining the chainable nature of querysets.
        """
        category_filter = CategoryFilter(self)
        queryset = self

        if filters:
            queryset = category_filter.apply_filters(filters)
        
        if search_query:
            queryset = category_filter.apply_search(search_query)
            
        if ordering:
            queryset = category_filter.apply_ordering(ordering)
            
        return queryset

    def with_counts(self):
        """Annotate categories with product counts."""
        return self.annotate(
            active_products_count=Count(
                'products',
                filter=Q(products__status='active', products__available=True)
            ),
            total_products_count=Count('products')
        )

    def ordered(self):
        """Get categories in display order."""
        return self.order_by('order')

    def active(self):
        """Get active categories."""
        return self.filter(is_active=True)

    def with_products(self):
        """Get categories that have active products."""
        return self.with_counts().filter(active_products_count__gt=0)

    def by_slug(self, slug: str):
        """Get category by slug."""
        return self.filter(slug=slug)

    def search(self, query: str):
        """Search categories by name or description."""
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

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

class NutritionQuerySet(models.QuerySet):
    def with_related(self):
        """Get queryset with related product."""
        return self.select_related('product')

    def by_category(self, category_id: Optional[uuid.UUID] = None):
        """Filter by category if provided."""
        if not category_id:
            return self
        return self.filter(product__category_id=category_id)

    def with_stats(self):
        """Get basic statistics for nutrition fields."""
        return self.aggregate(
            avg_calories=Avg('calories'),
            min_calories=Min('calories'),
            max_calories=Max('calories'),
            avg_proteins=Avg('proteins'),
            min_proteins=Min('proteins'),
            max_proteins=Max('proteins'),
            avg_carbs=Avg('carbohydrates'),
            min_carbs=Min('carbohydrates'),
            max_carbs=Max('carbohydrates'),
            avg_fats=Avg('fats'),
            min_fats=Min('fats'),
            max_fats=Max('fats'),
            avg_fiber=Avg('fiber'),
            min_fiber=Min('fiber'),
            max_fiber=Max('fiber')
        )

    def similar_to(self, nutrition_values: Dict[str, Decimal], tolerance: Decimal = Decimal('0.2')):
        """Find products with similar nutritional values."""
        query = Q()
        for field, value in nutrition_values.items():
            min_val = value * (1 - tolerance)
            max_val = value * (1 + tolerance)
            query &= Q(**{f"{field}__range": (min_val, max_val)})
        return self.filter(query)

    def with_dietary_restrictions(self, **preferences):
        """Filter by dietary preferences."""
        query = Q()
        for field, value in preferences.items():
            if field.startswith('min_') and value is not None:
                query &= Q(**{f"{field[4:]}__gte": value})
            elif field.startswith('max_') and value is not None:
                query &= Q(**{f"{field[4:]}__lte": value})
        return self.filter(query)

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