from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

@dataclass
class DomainEvent:
    """Base class for all domain events"""
    occurred_on: datetime = datetime.now()

@dataclass
class ProductCreated(DomainEvent):
    product_id: int
    name: str
    category_id: int

@dataclass
class ProductUpdated(DomainEvent):
    product_id: int
    changes: Dict[str, any]

@dataclass
class NutritionInfoUpdated(DomainEvent):
    product_id: int
    old_values: Dict[str, Decimal]
    new_values: Dict[str, Decimal]

@dataclass
class StockLevelChanged(DomainEvent):
    product_id: int
    old_quantity: int
    new_quantity: int
    reason: str

@dataclass
class CategoryOrderChanged(DomainEvent):
    category_id: int
    old_position: int
    new_position: int

@dataclass
class IngredientAllergenAdded(DomainEvent):
    ingredient_id: int
    allergen_id: int
