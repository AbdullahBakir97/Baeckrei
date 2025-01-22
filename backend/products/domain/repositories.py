from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet

from ..models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
from .value_objects import Money, Weight, NutritionValues, StockLevel

class IRepository(ABC):
    """Base repository interface"""
    @abstractmethod
    def get(self, id: int) -> Any:
        pass

    @abstractmethod
    def list(self, **filters) -> List[Any]:
        pass

    @abstractmethod
    def create(self, data: Dict) -> Any:
        pass

    @abstractmethod
    def update(self, id: int, data: Dict) -> Any:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

class IProductRepository(IRepository):
    """Product repository interface"""
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Product]:
        pass

    @abstractmethod
    def get_with_relations(self, id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def find_similar_nutrition(self, nutrition: NutritionValues, limit: int) -> List[Product]:
        pass

    @abstractmethod
    def update_stock(self, id: int, stock_level: StockLevel) -> Product:
        pass

class ICategoryRepository(IRepository):
    """Category repository interface"""
    @abstractmethod
    def get_active(self) -> QuerySet:
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Category]:
        pass

    @abstractmethod
    def update_order(self, id: int, new_order: int) -> Category:
        pass

class IIngredientRepository(IRepository):
    """Ingredient repository interface"""
    @abstractmethod
    def get_with_allergens(self, id: int) -> Optional[Ingredient]:
        pass

    @abstractmethod
    def get_commonly_used(self, limit: int) -> List[Ingredient]:
        pass

class IAllergenRepository(IRepository):
    """Allergen repository interface"""
    @abstractmethod
    def get_by_ingredient(self, ingredient_id: int) -> List[AllergenInfo]:
        pass

    @abstractmethod
    def get_by_category(self, category_id: int) -> List[AllergenInfo]:
        pass
