from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ..services.product_service import ProductService
from ..models import Product, Category
import uuid

class ProductController:
    """Controller class for handling product-related business logic."""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def get_product_list(self, filters: Dict[str, Any]) -> QuerySet[Product]:
        """Get filtered list of products."""
        # Extract filter parameters
        search_query = filters.get('search')
        category_id = filters.get('category')
        is_vegan = filters.get('vegan', False)
        is_vegetarian = filters.get('vegetarian', False)
        is_gluten_free = filters.get('gluten_free', False)
        exclude_allergens = filters.get('exclude_allergens', [])
        
        # Start with available products
        queryset = self.product_service.get_available_products()
        
        # Apply search if provided
        if search_query:
            queryset = self.product_service.search_products(search_query)
        
        # Apply category filter
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Apply dietary preferences
        if any([is_vegan, is_vegetarian, is_gluten_free]):
            queryset = self.product_service.get_products_by_dietary_preferences(
                is_vegan=is_vegan,
                is_vegetarian=is_vegetarian,
                is_gluten_free=is_gluten_free
            )
        
        # Exclude allergens if specified
        if exclude_allergens:
            queryset = self.product_service.get_products_by_allergens(exclude_allergens)
        
        return queryset.distinct()
    
    def get_product_detail(self, product_id: uuid.UUID) -> Optional[Product]:
        """Get product detail by ID."""
        product = self.product_service.get_by_id(product_id)
        if not product:
            raise ValidationError(f"Product with ID {product_id} not found")
        return product
    
    def get_featured_products(self, limit: int = 6) -> QuerySet[Product]:
        """Get featured products."""
        return self.product_service.get_featured_products(limit=limit)
    
    def create_product(self, data: Dict[str, Any]) -> Product:
        """Create a new product."""
        try:
            return self.product_service.create_product(data)
        except ValidationError as e:
            raise ValidationError(f"Invalid product data: {str(e)}")
    
    def update_product(self, product_id: uuid.UUID, data: Dict[str, Any]) -> Product:
        """Update an existing product."""
        product = self.get_product_detail(product_id)
        try:
            return self.product_service.update_product(product, data)
        except ValidationError as e:
            raise ValidationError(f"Invalid product data: {str(e)}")
    
    def delete_product(self, product_id: uuid.UUID) -> None:
        """Delete a product."""
        product = self.get_product_detail(product_id)
        try:
            self.product_service.delete(product)
        except Exception as e:
            raise ValidationError(f"Error deleting product: {str(e)}")
    
    def update_product_stock(self, product_id: uuid.UUID, quantity_change: int) -> Product:
        """Update product stock."""
        try:
            return self.product_service.update_stock(product_id, quantity_change)
        except ValidationError as e:
            raise ValidationError(f"Error updating stock: {str(e)}")
    
    def toggle_product_availability(self, product_id: uuid.UUID) -> Product:
        """Toggle product availability."""
        product = self.get_product_detail(product_id)
        return self.product_service.update(product, available=not product.available)
    
    def bulk_update_prices(self, price_updates: List[Dict[str, Any]]) -> None:
        """Bulk update product prices."""
        try:
            self.product_service.bulk_update_prices(price_updates)
        except Exception as e:
            raise ValidationError(f"Error updating prices: {str(e)}")
    
    def get_products_by_category(self, category: Category) -> QuerySet[Product]:
        """Get products by category."""
        return self.product_service.get_by_category(category)
    
    def generate_product_report(self) -> Dict[str, Any]:
        """Generate product report."""
        try:
            return self.product_service.generate_report()
        except Exception as e:
            raise ValidationError(f"Error generating report: {str(e)}")
