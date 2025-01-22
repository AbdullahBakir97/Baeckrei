"""
Product Management Services.
This module provides a unified interface for all product-related services.
"""

from .base import BaseService
from .product_service import ProductService
from .category_service import CategoryService
from .ingredient_allergen_service import IngredientAllergenService
from .PMS import ProductManagementService

# Export the unified service as the main interface
__all__ = [
    'ProductManagementService',  # Main service interface
    'ProductService',           # Individual services if needed
    'CategoryService',
    'IngredientAllergenService',
    'BaseService'              # Base service for extensions
]

# Create a default instance for easy import
default_service = ProductManagementService()