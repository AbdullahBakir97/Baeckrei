from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal

@dataclass
class Query:
    """Base query class"""
    pass

@dataclass
class GetProductQuery(Query):
    product_id: int

@dataclass
class ListProductsQuery(Query):
    category_id: Optional[int] = None
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    allergen_exclude: Optional[List[int]] = None
    page: int = 1
    page_size: int = 12
    order_by: str = "name"

@dataclass
class GetProductNutritionQuery(Query):
    product_id: int
    weight_grams: Optional[Decimal] = None

@dataclass
class FindSimilarProductsQuery(Query):
    product_id: int
    max_results: int = 5

@dataclass
class GetCategoryNutritionQuery(Query):
    category_id: int

@dataclass
class ListCategoriesQuery(Query):
    parent_id: Optional[int] = None
    include_inactive: bool = False

@dataclass
class SearchIngredientsQuery(Query):
    search_term: str
    exclude_allergens: Optional[List[int]] = None
    page: int = 1
    page_size: int = 10
