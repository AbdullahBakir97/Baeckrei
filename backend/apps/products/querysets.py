from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import uuid
from django.db import models
from django.db.models import Q, Avg, Min, Max, Count, F, Sum
import logging

logger = logging.getLogger(__name__)


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


class ProductQuerySet(models.QuerySet):
    """QuerySet class for Product model with optimized query methods."""

    def with_related(self):
        """Load all related fields for better performance."""
        logger.debug("Loading products with related fields")
        return self.select_related(
            'category',
            'nutrition_info'
        ).prefetch_related(
            'ingredients',
            'ingredients__allergens'
        )

    def available(self):
        """Filter available products."""
        logger.debug("Filtering available products")
        queryset = self.filter(
            available=True,
            status='active',
            category__is_active=True,
            stock__gt=0
        )
        logger.debug(f"Available products count: {queryset.count()}")
        return queryset

    def by_category(self, category_ids: Optional[List[uuid.UUID]] = None):
        """Filter products by category IDs."""
        if not category_ids:
            return self
        logger.debug(f"Filtering by categories: {category_ids}")
        queryset = self.filter(category_id__in=category_ids)
        logger.debug(f"Products in categories count: {queryset.count()}")
        return queryset

    def by_price_range(self, min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None):
        """Filter products by price range."""
        queryset = self
        if min_price is not None:
            logger.debug(f"Filtering by min price: {min_price}")
            queryset = queryset.filter(price__gte=min_price)
            logger.debug(f"After min price count: {queryset.count()}")
        if max_price is not None:
            logger.debug(f"Filtering by max price: {max_price}")
            queryset = queryset.filter(price__lte=max_price)
            logger.debug(f"After max price count: {queryset.count()}")
        return queryset

    def by_dietary_preferences(self, is_vegan=False, is_vegetarian=False, is_gluten_free=False):
        """Filter by dietary preferences."""
        queryset = self
        if is_vegan:
            queryset = queryset.filter(is_vegan=True)
        if is_vegetarian:
            queryset = queryset.filter(is_vegetarian=True)
        if is_gluten_free:
            queryset = queryset.filter(is_gluten_free=True)
        logger.debug(f"After dietary preferences count: {queryset.count()}")
        return queryset

    def search(self, query: str):
        """Search products by name, description, or category."""
        if not query:
            return self
        logger.debug(f"Searching products with query: {query}")
        queryset = self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        logger.debug(f"Search results count: {queryset.count()}")
        return queryset

    def featured(self, limit: int = 6):
        """Get featured products."""
        logger.debug("Getting featured products")
        return self.available().order_by('-created_at')[:limit]

    def related_products(self, product_id: uuid.UUID, limit: int = 4):
        """Get related products based on category."""
        logger.debug(f"Getting related products for product: {product_id}")
        try:
            product = self.get(id=product_id)
            queryset = self.available().filter(
                category=product.category
            ).exclude(
                id=product_id
            ).order_by('?')[:limit]
            logger.debug(f"Related products count: {queryset.count()}")
            return queryset
        except self.model.DoesNotExist:
            logger.warning(f"Product not found: {product_id}")
            return self.none()


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
