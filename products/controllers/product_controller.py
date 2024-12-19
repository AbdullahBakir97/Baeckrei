from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from ..services.product_service import ProductService
from ..models import Product

class ProductController:
    """Controller class for handling product-related business logic."""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def get_product_list(
        self,
        search_query: Optional[str] = None,
        category_slug: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        **filters
    ) -> QuerySet[Product]:
        """Get filtered list of products."""
        return self.product_service.search_products(
            query=search_query,
            category_slug=category_slug,
            min_price=min_price,
            max_price=max_price,
            **filters
        )
    
    def get_product_detail(self, product_id: str) -> Product:
        """Get product detail by ID."""
        return self.product_service.get_by_id(product_id)
    
    def get_featured_products(self) -> QuerySet[Product]:
        """Get featured products."""
        return self.product_service.get_featured_products()
    
    def create_product(self, data: Dict[str, Any]) -> Product:
        """Create a new product."""
        try:
            return self.product_service.create_product(**data)
        except ValidationError as e:
            raise ValidationError(f"Invalid product data: {str(e)}")
    
    def update_product(self, product_id: str, data: Dict[str, Any]) -> Product:
        """Update an existing product."""
        product = self.get_product_detail(product_id)
        try:
            return self.product_service.update_product(product, **data)
        except ValidationError as e:
            raise ValidationError(f"Invalid product data: {str(e)}")
    
    def delete_product(self, product_id: str) -> None:
        """Delete a product."""
        product = self.get_product_detail(product_id)
        self.product_service.delete(product)
    
    def toggle_product_availability(self, product_id: str) -> Product:
        """Toggle product availability."""
        product = self.get_product_detail(product_id)
        return self.product_service.toggle_availability(product)
