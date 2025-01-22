from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal

from ..models import Product, Category, Ingredient, AllergenInfo, NutritionInfo

class IProductService(ABC):
    @abstractmethod
    def create_product(self, data: Dict) -> Product:
        pass

    @abstractmethod
    def update_product(self, product_id: int, data: Dict) -> Product:
        pass

    @abstractmethod
    def delete_product(self, product_id: int) -> None:
        pass

    @abstractmethod
    def get_product_nutrition(self, product_id: int, weight_grams: Optional[Decimal] = None) -> Dict:
        pass

class IProductManagementService(ABC):
    @abstractmethod
    def create_product_with_relations(self, data: Dict) -> Product:
        pass

    @abstractmethod
    def update_product_with_relations(self, product_id: int, data: Dict) -> Product:
        pass

    @abstractmethod
    def get_filtered_products(self, **filters) -> List[Product]:
        pass

    @abstractmethod
    def get_product_full_details(self, product_id: int) -> Dict:
        pass

class INutritionService(ABC):
    @abstractmethod
    def calculate_nutrition(self, nutrition_data: Dict, weight_grams: Optional[Decimal] = None) -> Dict:
        pass

    @abstractmethod
    def find_similar_products(self, nutrition_values: Dict, max_results: int = 5) -> List[Product]:
        pass

    @abstractmethod
    def analyze_category_nutrition(self, category_id: int) -> Dict:
        pass

class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: 'DomainEvent') -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: callable) -> None:
        pass
