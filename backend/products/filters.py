"""
Product Management System Filters

This module contains filter classes for handling complex filtering, sorting,
and search operations across the product management system.
"""

from typing import Any, Dict, List, Optional, Type
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError
from . import EXCEPTIONS

class BaseFilter:
    """Base filter class with common filtering functionality."""
    
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        """Validate filter parameters."""
        return len(self.errors) == 0

    def apply_ordering(self, ordering: List[str]) -> QuerySet:
        """
        Apply ordering to queryset.
        
        Args:
            ordering: List of fields to order by. Prefix with '-' for descending.
            
        Returns:
            Ordered queryset
        """
        if not ordering:
            return self.queryset
            
        valid_fields = self.get_valid_ordering_fields()
        cleaned_ordering = []
        
        for field in ordering:
            desc = field.startswith('-')
            field_name = field[1:] if desc else field
            
            if field_name not in valid_fields:
                self.errors.setdefault('ordering', []).append(
                    f"Invalid ordering field: {field_name}"
                )
                continue
                
            cleaned_ordering.append(field)
            
        if self.errors:
            raise EXCEPTIONS.ValidationError(
                field='ordering',
                value=ordering,
                reason='Invalid ordering fields',
                message=f"Invalid ordering fields: {', '.join(self.errors['ordering'])}"
            )
            
        return self.queryset.order_by(*cleaned_ordering)

    def apply_search(self, search_query: Optional[str]) -> QuerySet:
        """
        Apply search filter to queryset.
        
        Args:
            search_query: Search term to filter by
            
        Returns:
            Filtered queryset
        """
        if not search_query:
            return self.queryset
            
        search_fields = self.get_search_fields()
        if not search_fields:
            return self.queryset
            
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})
            
        return self.queryset.filter(q_objects)

    def get_valid_ordering_fields(self) -> List[str]:
        """Get list of valid fields for ordering. Override in subclass."""
        return []

    def get_search_fields(self) -> List[str]:
        """Get list of fields to search. Override in subclass."""
        return []

class ProductFilter(BaseFilter):
    """Filter class for Product model."""
    
    def get_valid_ordering_fields(self) -> List[str]:
        return [
            'name',
            'price',
            'created_at',
            'stock',
            'category__name'
        ]
        
    def get_search_fields(self) -> List[str]:
        return [
            'name',
            'description',
            'category__name',
            'sku'
        ]
        
    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        queryset = self.queryset
        
        # Price range filter
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        if min_price is not None:
            try:
                min_price = float(min_price)
                if min_price < 0:
                    self.errors.setdefault('price', []).append(
                        "Minimum price cannot be negative"
                    )
                else:
                    queryset = queryset.filter(price__gte=min_price)
            except (TypeError, ValueError):
                self.errors.setdefault('price', []).append(
                    "Invalid minimum price value"
                )
                
        if max_price is not None:
            try:
                max_price = float(max_price)
                if max_price < 0:
                    self.errors.setdefault('price', []).append(
                        "Maximum price cannot be negative"
                    )
                elif min_price is not None and max_price < min_price:
                    self.errors.setdefault('price', []).append(
                        "Maximum price cannot be less than minimum price"
                    )
                else:
                    queryset = queryset.filter(price__lte=max_price)
            except (TypeError, ValueError):
                self.errors.setdefault('price', []).append(
                    "Invalid maximum price value"
                )
        
        # Category filter
        category_ids = filters.get('category_ids', [])
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)
            
        # Stock status filter
        stock_status = filters.get('stock_status')
        if stock_status:
            if stock_status == 'in_stock':
                queryset = queryset.filter(stock__gt=0)
            elif stock_status == 'out_of_stock':
                queryset = queryset.filter(stock=0)
            elif stock_status == 'low_stock':
                queryset = queryset.filter(stock__lte=F('min_stock_threshold'))
                
        # Dietary preferences
        if filters.get('is_vegan'):
            queryset = queryset.filter(is_vegan=True)
        if filters.get('is_vegetarian'):
            queryset = queryset.filter(is_vegetarian=True)
        if filters.get('is_gluten_free'):
            queryset = queryset.filter(is_gluten_free=True)
            
        # Allergen exclusions
        exclude_allergens = filters.get('exclude_allergens', [])
        if exclude_allergens:
            queryset = queryset.exclude(
                ingredients__allergens__id__in=exclude_allergens
            ).distinct()
            
        # Availability filter
        if filters.get('available_only', True):
            queryset = queryset.filter(
                available=True,
                status='active'
            )
            
        if self.errors:
            raise EXCEPTIONS.ValidationError(
                field='filters',
                value=filters,
                reason='Invalid filter parameters',
                message=str(self.errors)
            )
            
        return queryset

class CategoryFilter(BaseFilter):
    """Filter class for Category model."""
    
    def get_valid_ordering_fields(self) -> List[str]:
        return [
            'name',
            'order',
            'created_at',
            'products_count'
        ]
        
    def get_search_fields(self) -> List[str]:
        return [
            'name',
            'description',
            'slug'
        ]
        
    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        queryset = self.queryset
        
        # Active categories only
        if filters.get('active_only', True):
            queryset = queryset.filter(is_active=True)
            
        # Categories with products
        if filters.get('with_products'):
            queryset = queryset.annotate(
                products_count=Count('products')
            ).filter(products_count__gt=0)
            
        # Parent category filter
        parent_id = filters.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
            
        if self.errors:
            raise EXCEPTIONS.ValidationError(
                field='filters',
                value=filters,
                reason='Invalid filter parameters',
                message=str(self.errors)
            )
            
        return queryset

class IngredientFilter(BaseFilter):
    """Filter class for Ingredient model."""
    
    def get_valid_ordering_fields(self) -> List[str]:
        return [
            'name',
            'created_at',
            'usage_count'
        ]
        
    def get_search_fields(self) -> List[str]:
        return [
            'name',
            'description'
        ]
        
    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        queryset = self.queryset
        
        # Active ingredients only
        if filters.get('active_only', True):
            queryset = queryset.filter(is_active=True)
            
        # Filter by allergens
        allergen_ids = filters.get('allergen_ids', [])
        if allergen_ids:
            queryset = queryset.filter(allergens__id__in=allergen_ids)
            
        # Usage filter
        if filters.get('used_only'):
            queryset = queryset.annotate(
                usage_count=Count('products')
            ).filter(usage_count__gt=0)
            
        if self.errors:
            raise EXCEPTIONS.ValidationError(
                field='filters',
                value=filters,
                reason='Invalid filter parameters',
                message=str(self.errors)
            )
            
        return queryset
