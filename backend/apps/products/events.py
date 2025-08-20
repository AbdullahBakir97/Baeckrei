"""
Domain events for the products module.
"""
from django.dispatch import Signal
from typing import Dict, Any

# Product Events
ProductCreated = Signal()  # Provides kwargs: product
ProductUpdated = Signal()  # Provides kwargs: product
ProductDeleted = Signal()  # Provides kwargs: product_data
StockUpdated = Signal()   # Provides kwargs: product, quantity_change, reason
IngredientsUpdated = Signal()  # Provides kwargs: product
NutritionUpdated = Signal()    # Provides kwargs: product

# Category Events
CategoryCreated = Signal()  # Provides kwargs: category
CategoryUpdated = Signal()  # Provides kwargs: category
CategoryDeleted = Signal()  # Provides kwargs: category_data

# Ingredient Events
IngredientCreated = Signal()  # Provides kwargs: ingredient
IngredientUpdated = Signal()  # Provides kwargs: ingredient
IngredientDeleted = Signal()  # Provides kwargs: ingredient_data

# Allergen Events
AllergenCreated = Signal()  # Provides kwargs: allergen
AllergenUpdated = Signal()  # Provides kwargs: allergen
AllergenDeleted = Signal()  # Provides kwargs: allergen_data

# Stock Events
LowStockAlert = Signal()    # Provides kwargs: product, current_stock, min_stock
OutOfStockAlert = Signal()  # Provides kwargs: product
