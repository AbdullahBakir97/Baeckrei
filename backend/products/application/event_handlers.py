from typing import Dict, Any
import logging
from django.db import transaction
from django.core.cache import cache

from ..domain.events import (
    ProductCreated, ProductUpdated, NutritionInfoUpdated,
    StockLevelChanged, CategoryOrderChanged, IngredientAllergenAdded
)
from ..infrastructure.cache import ProductCache, CategoryCache
from ..domain.repositories import (
    IProductRepository, ICategoryRepository,
    IIngredientRepository, IAllergenRepository
)

logger = logging.getLogger(__name__)

class EventHandler:
    """Base event handler class"""
    def __init__(self, repositories: Dict[str, Any]):
        self.repositories = repositories

    def handle(self, event: Any) -> None:
        """Handle the event"""
        method_name = f"handle_{event.__class__.__name__}"
        handler = getattr(self, method_name, None)
        if handler:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling event {event.__class__.__name__}: {str(e)}")
                raise

class ProductEventHandler(EventHandler):
    def handle_ProductCreated(self, event: ProductCreated) -> None:
        """Handle product creation event"""
        logger.info(f"Product created: {event.product_id}")
        
        # Invalidate relevant caches
        ProductCache.invalidate_product(event.product_id)
        CategoryCache.invalidate_tree()

    def handle_ProductUpdated(self, event: ProductUpdated) -> None:
        """Handle product update event"""
        logger.info(f"Product updated: {event.product_id}")
        
        # Invalidate caches
        ProductCache.invalidate_product(event.product_id)
        if 'category_id' in event.changes:
            CategoryCache.invalidate_tree()

    def handle_NutritionInfoUpdated(self, event: NutritionInfoUpdated) -> None:
        """Handle nutrition info update event"""
        logger.info(f"Nutrition info updated for product: {event.product_id}")
        
        # Invalidate product cache
        ProductCache.invalidate_product(event.product_id)

    def handle_StockLevelChanged(self, event: StockLevelChanged) -> None:
        """Handle stock level change event"""
        logger.info(
            f"Stock level changed for product {event.product_id}: "
            f"{event.old_quantity} -> {event.new_quantity}"
        )
        
        # Invalidate product cache
        ProductCache.invalidate_product(event.product_id)

class CategoryEventHandler(EventHandler):
    def handle_CategoryOrderChanged(self, event: CategoryOrderChanged) -> None:
        """Handle category order change event"""
        logger.info(
            f"Category {event.category_id} order changed: "
            f"{event.old_position} -> {event.new_position}"
        )
        
        # Invalidate category tree cache
        CategoryCache.invalidate_tree()

class IngredientEventHandler(EventHandler):
    def handle_IngredientAllergenAdded(self, event: IngredientAllergenAdded) -> None:
        """Handle ingredient allergen addition event"""
        logger.info(
            f"Allergen {event.allergen_id} added to ingredient {event.ingredient_id}"
        )
        
        # Get all products using this ingredient
        products = self.repositories['product_repository'].list(
            ingredients__id=event.ingredient_id
        )
        
        # Invalidate cache for all affected products
        for product in products:
            ProductCache.invalidate_product(product.id)
