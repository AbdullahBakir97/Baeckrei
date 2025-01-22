from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class Command:
    """Base command class"""
    timestamp: datetime = datetime.now()

@dataclass
class CreateProductCommand(Command):
    name: str
    category_id: int
    description: Optional[str] = None
    price: Optional[Decimal] = None
    ingredients: Optional[List[int]] = None
    allergens: Optional[List[int]] = None
    nutrition_info: Optional[Dict] = None

@dataclass
class UpdateProductCommand(Command):
    product_id: int
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    ingredients: Optional[List[int]] = None
    allergens: Optional[List[int]] = None
    nutrition_info: Optional[Dict] = None

@dataclass
class DeleteProductCommand(Command):
    product_id: int

@dataclass
class UpdateStockCommand(Command):
    product_id: int
    quantity: int
    reason: str

@dataclass
class CreateCategoryCommand(Command):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

@dataclass
class UpdateCategoryOrderCommand(Command):
    category_id: int
    new_order: int

@dataclass
class AddIngredientCommand(Command):
    name: str
    allergens: Optional[List[int]] = None

@dataclass
class UpdateIngredientAllergensCommand(Command):
    ingredient_id: int
    allergen_ids: List[int]
