"""
Product Management System Filters

This module contains filter classes for handling complex filtering, sorting,
and search operations across the product management system.
"""

from typing import Any, Dict, List, Optional, Type
from django.db.models import Q, QuerySet, Count, F
from django.core.exceptions import ValidationError
from apps.products.exceptions import EXCEPTIONS
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class BaseFilter:
    """Base filter class with common filtering functionality."""
    
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset
        self.errors: Dict[str, List[str]] = {}

    def validate(self) -> bool:
        """Validate filter parameters."""
        return len(self.errors) == 0

    def add_error(self, field: str, message: str) -> None:
        """Add an error message for a field."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)

    def _apply_search(self, search_term: str, fields: List[str]) -> QuerySet:
        """Apply search filter across specified fields."""
        if not search_term:
            return self.queryset

        try:
            q_objects = Q()
            for field in fields:
                q_objects |= Q(**{f"{field}__icontains": search_term})
            return self.queryset.filter(q_objects)
        except Exception as e:
            raise EXCEPTIONS.InvalidSearchError(term=search_term, message=str(e))

    def _apply_ordering(self, ordering: str, valid_fields: List[str]) -> QuerySet:
        """Apply ordering to queryset."""
        if not ordering:
            return self.queryset

        try:
            order_fields = []
            for field in ordering.split(','):
                field = field.strip()
                if field.startswith('-'):
                    clean_field = field[1:]
                else:
                    clean_field = field

                if clean_field not in valid_fields:
                    raise EXCEPTIONS.InvalidOrderingError(field=clean_field)
                order_fields.append(field)

            return self.queryset.order_by(*order_fields)
        except EXCEPTIONS.InvalidOrderingError:
            raise
        except Exception as e:
            raise EXCEPTIONS.InvalidOrderingError(message=str(e))

class ProductFilter(BaseFilter):
    """Filter class for Product model."""
    
    def __init__(self, queryset):
        self.queryset = queryset
        self.errors = {}
        
    def get_search_fields(self):
        """Get fields to search in."""
        return ['name', 'description', 'category__name']
    
    def add_error(self, field: str, message: str):
        """Add an error message for a field."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
        
    def _apply_search(self, search_term: str, fields: List[str]) -> QuerySet:
        """Apply search filter across specified fields."""
        if not search_term:
            return self.queryset
            
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": search_term})
        return self.queryset.filter(q_objects)
    
    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        try:
            if not isinstance(filters, dict):
                filters = dict(filters)
            
            logger.debug(f"Applying filters: {filters}")
            logger.debug(f"Initial queryset count: {self.queryset.count()}")
            
            # Category filter
            category_ids = filters.get('category_ids')
            if category_ids:
                try:
                    category_list = [int(id) for id in category_ids.split(',')]
                    self.queryset = self.queryset.filter(category__id__in=category_list)
                    logger.debug(f"After category filter count: {self.queryset.count()}")
                except (ValueError, TypeError):
                    self.add_error('category', "Invalid category ID format")
            
            # Price range filter
            price_lte = filters.get('price__lte')
            price_gte = filters.get('price__gte')
            
            if price_lte is not None:
                try:
                    price_lte = Decimal(str(price_lte))
                    if price_lte < 0:
                        self.add_error('price', "Maximum price cannot be negative")
                    else:
                        self.queryset = self.queryset.filter(price__lte=price_lte)
                        logger.debug(f"After price_lte filter count: {self.queryset.count()}")
                except (TypeError, ValueError, InvalidOperation):
                    self.add_error('price', "Invalid maximum price value")
            
            if price_gte is not None:
                try:
                    price_gte = Decimal(str(price_gte))
                    if price_gte < 0:
                        self.add_error('price', "Minimum price cannot be negative")
                    elif price_lte is not None and price_gte > price_lte:
                        self.add_error('price', "Minimum price cannot be greater than maximum price")
                    else:
                        self.queryset = self.queryset.filter(price__gte=price_gte)
                        logger.debug(f"After price_gte filter count: {self.queryset.count()}")
                except (TypeError, ValueError, InvalidOperation):
                    self.add_error('price', "Invalid minimum price value")
            
            # Dietary preferences
            if filters.get('is_vegan'):
                self.queryset = self.queryset.filter(is_vegan=True)
                logger.debug(f"After vegan filter count: {self.queryset.count()}")
            
            if filters.get('is_vegetarian'):
                self.queryset = self.queryset.filter(is_vegetarian=True)
                logger.debug(f"After vegetarian filter count: {self.queryset.count()}")
            
            if filters.get('is_gluten_free'):
                self.queryset = self.queryset.filter(is_gluten_free=True)
                logger.debug(f"After gluten-free filter count: {self.queryset.count()}")
            
            # Stock filter
            if filters.get('in_stock'):
                self.queryset = self.queryset.filter(stock__gt=0)
                logger.debug(f"After stock filter count: {self.queryset.count()}")
            
            # Search filter
            search_term = filters.get('search')
            if search_term:
                self.queryset = self._apply_search(search_term, self.get_search_fields())
                logger.debug(f"After search filter count: {self.queryset.count()}")
            
            if self.errors:
                raise EXCEPTIONS.FilterError(self.errors)
            
            return self.queryset
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            raise

class CategoryFilter(BaseFilter):
    """Filter class for Category model."""

    def get_valid_ordering_fields(self) -> List[str]:
        """Get list of valid ordering fields."""
        return ['name', 'created_at', 'updated_at', 'products_count']

    def get_search_fields(self) -> List[str]:
        """Get list of searchable fields."""
        return ['name', 'description', 'slug']

    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        try:
            # Apply search if present
            search_term = filters.get('search')
            if search_term:
                self.queryset = self._apply_search(search_term, self.get_search_fields())

            # Active categories only
            if filters.get('active_only', True):
                self.queryset = self.queryset.filter(is_active=True)
            
            # Categories with products
            if filters.get('with_products'):
                self.queryset = self.queryset.annotate(
                    products_count=Count('products')
                ).filter(products_count__gt=0)
            
            # Parent category filter
            parent_id = filters.get('parent_id')
            if parent_id:
                self.queryset = self.queryset.filter(parent_id=parent_id)
            
            # Apply ordering
            ordering = filters.get('ordering')
            if ordering:
                self.queryset = self._apply_ordering(ordering, self.get_valid_ordering_fields())

            if not self.validate():
                raise EXCEPTIONS.InvalidFilterError(errors=self.errors)

            return self.queryset

        except EXCEPTIONS.FilterError:
            raise
        except Exception as e:
            raise EXCEPTIONS.InvalidFilterError(message=f"Error filtering categories: {str(e)}")

class IngredientFilter(BaseFilter):
    """Filter class for Ingredient model."""

    def get_valid_ordering_fields(self) -> List[str]:
        """Get list of valid ordering fields."""
        return ['name', 'created_at', 'updated_at', 'usage_count']

    def get_search_fields(self) -> List[str]:
        """Get list of searchable fields."""
        return ['name', 'description']

    def apply_filters(self, filters: Dict[str, Any]) -> QuerySet:
        """Apply all filters to queryset."""
        try:
            # Apply search if present
            search_term = filters.get('search')
            if search_term:
                self.queryset = self._apply_search(search_term, self.get_search_fields())

            # Active ingredients only
            if filters.get('active_only', True):
                self.queryset = self.queryset.filter(is_active=True)
            
            # Filter by allergens
            allergen_ids = filters.get('allergen_ids', [])
            if allergen_ids:
                self.queryset = self.queryset.filter(allergens__id__in=allergen_ids)
            
            # Usage filter
            if filters.get('used_only'):
                self.queryset = self.queryset.annotate(
                    usage_count=Count('products')
                ).filter(usage_count__gt=0)
            
            # Apply ordering
            ordering = filters.get('ordering')
            if ordering:
                self.queryset = self._apply_ordering(ordering, self.get_valid_ordering_fields())

            if not self.validate():
                raise EXCEPTIONS.InvalidFilterError(errors=self.errors)

            return self.queryset

        except EXCEPTIONS.FilterError:
            raise
        except Exception as e:
            raise EXCEPTIONS.InvalidFilterError(message=f"Error filtering ingredients: {str(e)}")
