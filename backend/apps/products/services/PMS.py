from typing import List, Dict, Any, Optional, Union
from django.db import transaction
from django.db.models import Sum, F, Q, Count, QuerySet
from .. import EXCEPTIONS
from ..models import (
    Product,
    Category,
    Ingredient,
    AllergenInfo,
)
from .product_service import ProductService
from .category_service import CategoryService
import uuid
from decimal import Decimal

class ProductManagementService:
    """
    Unified service for managing all product-related operations.
    Provides a single entry point for product, category, ingredient, and allergen operations.
    Handles business logic and data operations without serialization concerns.
    """
    
    def __init__(self):
        """Initialize service instances."""
        self.products = ProductService()
        self.categories = CategoryService()
    
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that required fields are present in the data."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise EXCEPTIONS.ValidationError(
                field='required_fields',
                value=missing_fields,
                reason='Missing required fields',
                message=f"Missing required fields: {', '.join(missing_fields)}"
            )

    # Product Operations
    def _handle_category(self, data: Dict[str, Any]) -> Optional[Category]:
        """Handle category creation or retrieval."""
        category_data = data.pop('category', None)
        if not category_data:
            return None

        if 'id' in category_data:
            category = self.categories.get_by_id(category_data['id'])
            if not category:
                raise EXCEPTIONS.CategoryNotFoundError(
                    category_id=category_data['id'],
                    message=f"Category with ID '{category_data['id']}' not found"
                )
        else:
            if 'name' not in category_data:
                raise EXCEPTIONS.ValidationError(
                    field='category',
                    value=category_data,
                    reason='Missing required field "name" for category creation'
                )
            category = self.categories.create_category(category_data)
        
        return category

    def get_related_products(self, product_id: uuid.UUID, limit: int = 4) -> QuerySet[Product]:
        """
        Get related products based on category and dietary preferences.
        
        Args:
            product_id: UUID of the product to find related items for
            limit: Maximum number of related products to return (default: 4)
            
        Returns:
            QuerySet of related products
            
        Raises:
            ProductNotFoundError: If product doesn't exist
        """
        return self.products.get_related_products(product_id, limit)

    @transaction.atomic
    def create_product_with_relations(self, data: Dict[str, Any], strict: bool = False) -> Product:
        """
        Create a product with optional relations.
        
        Args:
            data: Product data which may include:
                - Basic product info (name, price, etc.)
                - category: Category data or ID
                - nutrition_info: Nutrition data (optional)
                - ingredients: Ingredient data (optional)
            strict: If True, fails if any additional info (nutrition/ingredients) fails to be added
                   If False, creates product even if additional info fails (default)
        
        Returns:
            Created product instance
            
        Note:
            When strict=False and additional info fails, the error will be logged but the
            product will still be created. You can add the additional info later using
            add_product_nutrition() or update_product_ingredients().
        """
        try:
            # Validate required fields
            required_fields = ['name', 'price']
            self.validate_data(data, required_fields)
            
            # Create a copy of data to avoid modifying the input
            product_data = data.copy()
            
            # Extract additional data
            nutrition_data = product_data.pop('nutrition_info', None)
            ingredient_data = product_data.pop('ingredients', None)
            
            # Handle category
            category = self._handle_category(product_data)
            if category:
                product_data['category'] = category
            
            # Create base product first
            product = self.products.create_product(product_data)
            
            # Track any errors with additional info
            errors = []
            
            # Add nutrition info if provided
            if nutrition_data:
                try:
                    product = self.products.add_product_nutrition(product.id, nutrition_data)
                except Exception as e:
                    errors.append(f"Failed to add nutrition info: {str(e)}")
                    if strict:
                        raise
            
            # Add ingredients if provided
            if ingredient_data:
                try:
                    product = self.products.update_product_ingredients(product.id, ingredient_data)
                except Exception as e:
                    errors.append(f"Failed to add ingredients: {str(e)}")
                    if strict:
                        raise
            
            # If in strict mode and we had errors, clean up and raise the first error
            if strict and errors:
                self.products.delete_product(product)
                raise EXCEPTIONS.ProductError(
                    message=errors[0],
                    code="PRODUCT_CREATION_ERROR"
                )
            
            # If not in strict mode, return the product even if some additional info failed
            return product
            
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.CategoryNotFoundError,
                EXCEPTIONS.ProductNotFoundError, EXCEPTIONS.IngredientNotFoundError,
                EXCEPTIONS.AllergenNotFoundError, EXCEPTIONS.NutritionValidationError):
            # Re-raise validation and category errors
            raise
        except Exception as e:
            # Convert any other errors to ProductError
            raise EXCEPTIONS.ProductError(
                message=f"Error creating product with relations: {str(e)}",
                code="PRODUCT_CREATE_ERROR"
            )

    @transaction.atomic
    def add_product_nutrition(self, product_id: uuid.UUID, nutrition_data: Dict[str, Any], weight_grams: Optional[Decimal] = None) -> Product:
        """Add or update nutrition information for a product."""
        return self.products.add_product_nutrition(product_id, nutrition_data, weight_grams)

    @transaction.atomic
    def add_product_ingredients(self, product_id: uuid.UUID, ingredient_data: List[uuid.UUID]) -> Product:
        """Add ingredients to an existing product."""
        return self.products.update_product_ingredients(product_id, ingredient_data)

    @transaction.atomic
    def update_product_with_relations(self, product_id: uuid.UUID, data: Dict[str, Any]) -> Product:
        """
        Update a product and its relations.
        
        Args:
            product_id: ID of the product to update
            data: Updated product data including optional category, ingredients, and nutrition info
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            CategoryNotFoundError: If category ID is invalid
            ValidationError: If category data is invalid
            NutritionValidationError: If nutrition data is invalid
        """
        try:
            # Validate product exists first
            product = self.products.get_by_id(product_id)
            if not product:
                raise EXCEPTIONS.ProductNotFoundError(
                    product_id=product_id,
                    message=f"Cannot update product: Product with ID '{product_id}' not found"
                )
            
            # Handle category update
            category_data = data.pop('category', None)
            if category_data:
                if 'id' in category_data:
                    category = self.categories.get_by_id(category_data['id'])
                    if not category:
                        raise EXCEPTIONS.CategoryNotFoundError(
                            category_id=category_data['id'],
                            message=f"Cannot update product: Category with ID '{category_data['id']}' not found"
                        )
                else:
                    # Validate category data
                    if 'name' not in category_data:
                        raise EXCEPTIONS.ValidationError(
                            field='category',
                            value=category_data,
                            reason='Missing required field "name" for category creation'
                        )
                    category = self.categories.create_category(category_data)
                data['category'] = category

            # Handle nutrition info update if provided
            nutrition_data = data.get('nutrition_info')
            if nutrition_data is not None:
                self.products.update_product_nutrition(product_id, nutrition_data)
            
            # Update product with ingredients
            return self.products.update_product_with_ingredients(product_id, data)
            
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.CategoryNotFoundError,
                EXCEPTIONS.ProductNotFoundError, EXCEPTIONS.IngredientNotFoundError,
                EXCEPTIONS.AllergenNotFoundError, EXCEPTIONS.NutritionValidationError):
            # Re-raise known errors
            raise
        except Exception as e:
            # Convert any other errors to ProductError
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product with relations: {str(e)}",
                code="PRODUCT_UPDATE_ERROR"
            )
    
    @transaction.atomic
    def delete_product(self, product_id: uuid.UUID) -> None:
        """Delete a product and handle its relations."""
        product = self.products.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)
        
        # Remove ingredient associations
        product.ingredients.clear()
        # Delete the product
        product.delete()

    def get_product_details(self, product_id: uuid.UUID) -> Dict[str, Any]:
        """Get product details with caching."""
        return self.products.get_product(product_id)

    def get_product_full_details(self, product_id: str) -> Dict[str, Any]:
        """Get complete product details including category, ingredients, allergens, and nutrition."""
        try:
            # Convert string to UUID
            if isinstance(product_id, str):
                try:
                    product_uuid = uuid.UUID(product_id)
                except ValueError:
                    raise EXCEPTIONS.ValidationError(
                        field="product_id",
                        value=product_id,
                        reason="Invalid UUID format",
                        message=f"The provided ID '{product_id}' is not a valid UUID"
                    )
            else:
                product_uuid = product_id

            # Use with_related() to efficiently load all related data
            product = self.products.get_queryset().with_related().filter(id=product_uuid).first()
            if not product:
                raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)
                
            return {
                'product': product,
                'category': product.category,
                'ingredients': list(product.ingredients.all()),
                'allergens': list(product.allergens),
                'nutrition': product.nutrition_info,
                'stock_status': {
                    'is_low_stock': product.stock == 0,
                    'needs_restock': product.stock == 0,
                    'stock_level': product.stock
                }
            }
        except EXCEPTIONS.ValidationError:
            raise
        except ValueError as e:
            raise EXCEPTIONS.ValidationError(
                field="product_id",
                value=product_id,
                reason=str(e),
                message=f"Invalid product ID format: {str(e)}"
            )
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error retrieving product details: {str(e)}",
                code="PRODUCT_RETRIEVAL_ERROR"
            )

    def get_filtered_products(self, 
                            category_ids: Optional[List[uuid.UUID]] = None,
                            price_range: Optional[Dict[str, float]] = None,
                            dietary_prefs: Optional[Dict[str, bool]] = None,
                            allergen_exclusions: Optional[List[uuid.UUID]] = None,
                            search_query: Optional[str] = None,
                            ordering: Optional[List[str]] = None,
                            limit: Optional[int] = None) -> QuerySet[Product]:
        """Get products with comprehensive filtering options."""
        # Get base filtered products
        products = self.products.get_available_products(
            category_ids=category_ids,
            price_range=price_range,
            dietary_prefs=dietary_prefs,
            search_query=search_query,
            ordering=ordering
        )
        
        # Apply allergen exclusions if specified
        if allergen_exclusions:
            products = (
                products.exclude(ingredients__allergens__id__in=allergen_exclusions)
                .with_related()  # Ensure related data is fetched
                .distinct()
            )
        
        if limit:
            products = products[:limit]
        
        return products

    def generate_report(self, report_type: str = 'all', **kwargs) -> Dict[str, Any]:
        """Generate comprehensive reports based on type."""
        if report_type == 'inventory':
            base_report = self.products.generate_inventory_report()
            
            # Add category-specific inventory insights
            category_insights = (
                self.categories.get_queryset()
                .with_product_stats()
                .values(
                    'name', 'total_stock', 'total_value',
                    'low_stock_count', 'out_of_stock_count'
                )
            )
            
            # Get ingredient availability impact
            ingredient_insights = (
                self.products.ingredient_service.get_queryset()
                .with_product_stats()
                .filter(affected_products__gt=0)
                .values('name', 'affected_products')
            )
            
            report = {
                **base_report,
                'category_insights': list(category_insights),
                'ingredient_insights': list(ingredient_insights),
                'recommendations': self._generate_inventory_recommendations(base_report)
            }
            
            # Add summary metrics
            report['summary'] = {
                'total_items': sum(item['stock'] for item in base_report.get('low_stock_items', [])),
                'total_value': base_report.get('stock_value', {}).get('total_value', 0),
                'low_stock_categories': sum(1 for cat in category_insights if cat['low_stock_count'] > 0),
                'affected_ingredients': len(ingredient_insights)
            }
            return report
            
        elif report_type == 'complete':
            return {
                'products': self.products.get_product_statistics(),
                'categories': self.categories.get_statistics(),
                'ingredients': self.products.ingredient_service.get_ingredient_statistics(),
                'allergens': self.products.ingredient_service.get_allergen_statistics()
            }
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_inventory_recommendations(self, inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate inventory recommendations based on current state."""
        recommendations = []
        
        # Check low stock items
        if inventory['low_stock_items']:
            recommendations.append({
                'type': 'restock',
                'priority': 'high',
                'message': f"Restock {len(inventory['low_stock_items'])} items below minimum stock level",
                'items': inventory['low_stock_items']
            })
        
        # Check overstocked items
        if inventory['overstocked_items']:
            recommendations.append({
                'type': 'reduce_stock',
                'priority': 'medium',
                'message': f"Consider reducing stock for {len(inventory['overstocked_items'])} overstocked items",
                'items': inventory['overstocked_items']
            })
        
        # Check stock value distribution
        stock_value = inventory['stock_value']
        if stock_value['total_value'] > 0:
            recommendations.append({
                'type': 'value_distribution',
                'priority': 'low',
                'message': "Review stock value distribution",
                'details': {
                    'total_value': stock_value['total_value'],
                    'avg_item_value': stock_value['avg_item_value']
                }
            })
        
        return recommendations
    
    # Bulk Operations
    @transaction.atomic
    def bulk_update_products(self, updates: List[Dict[str, Any]]) -> None:
        """Bulk update products and their relations."""
        for update in updates:
            product_id = update.pop('id')
            product = self.products.get_by_id(product_id)
            if product:
                if 'price' in update:
                    self.products.update_product(product, {'price': update['price']})
                if 'ingredients' in update:
                    # Update ingredients for the product
                    self.products.update_product_ingredients(
                        product.id, 
                        update['ingredients']
                    )
    
    @transaction.atomic
    def bulk_update_stock(self, stock_updates: List[Dict[str, Any]]) -> None:
        """Bulk update product stock levels."""
        for update in stock_updates:
            try:
                self.products.update_stock(
                    update['product_id'],
                    update['quantity_change']
                )
            except EXCEPTIONS.InsufficientStockError as e:
                # Add update details to the error
                e.message = f"Stock update failed: {e.message}"
                raise
    
    def search_all(self, query: str) -> Dict[str, Any]:
        """Search across all entities."""
        return {
            'products': self.products.search(query),
            'categories': self.categories.search(query),
            'ingredients': self.products.ingredient_service.search(query),
            'allergens': self.products.ingredient_service.search(query)
        }

    # Additional helper methods
    def get_product_allergens(self, product_id: uuid.UUID) -> List[AllergenInfo]:
        """Get all allergens associated with a product through its ingredients."""
        product = self.products.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)
        
        ingredient_ids = [ingredient.id for ingredient in product.ingredients.all()]
        return self.products.ingredient_service.get_allergens_for_ingredients(ingredient_ids)
    
    def get_category_allergens(self, category_id: uuid.UUID) -> List[AllergenInfo]:
        """Get all allergens associated with products in a category."""
        category = self.categories.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(category_id=category_id)
        
        return self.products.ingredient_service.get_category_allergens(category_id)

    # Category Operations
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> Category:
        """Create a new category."""
        return self.categories.create_category(data)
    
    @transaction.atomic
    def update_category(self, category_id: uuid.UUID, data: Dict[str, Any]) -> Category:
        """Update a category."""
        category = self.categories.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(category_id=category_id)
        return self.categories.update_category(category, data)
    
    @transaction.atomic
    def delete_category(self, category_id: uuid.UUID) -> None:
        """Delete a category and handle its products."""
        category = self.categories.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(category_id=category_id)
        
        # Check if category has products
        products_count = category.products.count()
        if products_count > 0:
            raise EXCEPTIONS.CategoryInUseError(
                category_id=category_id,
                product_count=products_count
            )
        
        category.delete()
    
    def get_category_products_summary(self, category_id: str) -> Dict[str, Any]:
        """Get a summary of products in a category with their ingredients and allergens."""
        category = self.categories.get_by_id(category_id)
        if not category:
            raise EXCEPTIONS.CategoryNotFoundError(category_id=category_id)
            
        products = self.products.get_available_products(category_ids=[category_id])
        
        return {
            'category': category,
            'products_count': products.count(),
            'active_products': products,
            'common_allergens': self.products.ingredient_service.get_allergens_in_category(category_id)
        }

    @transaction.atomic
    def update_category_order(self, order_data: List[Dict[str, Any]]) -> None:
        """Update category display order."""
        self.categories.reorder_categories(order_data)
    
    # Ingredient Operations
    @transaction.atomic
    def create_ingredient(self, data: Dict[str, Any]) -> Ingredient:
        """Create a new ingredient with allergens."""
        return self.products.ingredient_service.create_ingredient_with_allergens(data)
    
    @transaction.atomic
    def update_ingredient(self, ingredient_id: uuid.UUID, data: Dict[str, Any]) -> Ingredient:
        """Update an ingredient and its allergens."""
        ingredient = self.products.ingredient_service.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
        
        return self.products.ingredient_service.update_ingredient_with_allergens(ingredient_id, data)
    
    @transaction.atomic
    def delete_ingredient(self, ingredient_id: uuid.UUID) -> None:
        """Delete an ingredient and handle its relations."""
        ingredient = self.products.ingredient_service.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
        
        # Get ingredient statistics to check usage
        ingredient_stats = self.products.ingredient_service.get_ingredient_statistics()
        ingredient_info = next((i for i in ingredient_stats.get('most_used', []) if str(i['id']) == str(ingredient_id)), {})
        products_count = ingredient_info.get('usage_count', 0)
        
        if products_count > 0:
            raise EXCEPTIONS.IngredientInUseError(
                ingredient_id=ingredient_id,
                product_count=products_count
            )
        
        # Remove allergen associations and delete
        ingredient.allergens.clear()
        ingredient.delete()
    
    def get_ingredient_details(self, ingredient_id: int) -> Dict[str, Any]:
        """Get detailed ingredient information including allergens and usage."""
        ingredient = self.products.ingredient_service.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            raise EXCEPTIONS.IngredientNotFoundError(ingredient_id=ingredient_id)
        
        # Get ingredient statistics for usage count
        ingredient_stats = self.products.ingredient_service.get_ingredient_statistics()
        ingredient_info = next((i for i in ingredient_stats.get('most_used', []) if str(i['id']) == str(ingredient_id)), {})
        usage_count = ingredient_info.get('usage_count', 0)
        
        return {
            'ingredient': ingredient,
            'allergens': ingredient.allergens.all(),
            'usage_count': usage_count,
            'products': self.products.get_products_by_ingredient(ingredient_id).filter(available=True)
        }
    
    @transaction.atomic
    def update_ingredient_allergens(self, ingredient_id: int, allergen_ids: List[int]) -> Ingredient:
        """Update ingredient allergens."""
        return self.products.ingredient_service.set_ingredient_allergens(ingredient_id, allergen_ids)
    
    # Allergen Operations
    @transaction.atomic
    def create_allergen(self, data: Dict[str, Any]) -> AllergenInfo:
        """Create a new allergen."""
        return self.products.ingredient_service.create_allergen(data)
    
    @transaction.atomic
    def update_allergen(self, allergen_id: uuid.UUID, data: Dict[str, Any]) -> AllergenInfo:
        """Update an allergen."""
        allergen = self.products.ingredient_service.get_allergen_by_id(allergen_id)
        if not allergen:
            raise EXCEPTIONS.AllergenNotFoundError(allergen_id=allergen_id)
        return self.products.ingredient_service.update_allergen(allergen_id, data)
    
    @transaction.atomic
    def delete_allergen(self, allergen_id: uuid.UUID) -> None:
        """Delete an allergen and handle its relations."""
        allergen = self.products.ingredient_service.get_allergen_by_id(allergen_id)
        if not allergen:
            raise EXCEPTIONS.AllergenNotFoundError(allergen_id=allergen_id)
        
        # Get allergen statistics to check usage
        allergen_stats = self.products.ingredient_service.get_allergen_statistics()
        allergen_info = next((a for a in allergen_stats.get('most_common', []) if str(a['id']) == str(allergen_id)), {})
        ingredients_count = allergen_info.get('ingredient_count', 0)
        
        if ingredients_count > 0:
            raise EXCEPTIONS.AllergenInUseError(
                allergen_id=allergen_id,
                ingredient_count=ingredients_count,
                message=f"Cannot delete allergen that is used in {ingredients_count} ingredients"
            )
        
        self.products.ingredient_service.delete_allergen(allergen_id)
    
    # Nutrition Operations
    def get_product_nutrition(self,
                            product_id: uuid.UUID,
                            weight_grams: Optional[Decimal] = None,
                            diet_type: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive nutrition information for a product."""
        return self.products.get_product_nutrition(
            product_id=product_id,
            weight_grams=weight_grams,
            diet_type=diet_type
        )

    def find_similar_nutrition_products(self,
                                      product_id: uuid.UUID,
                                      diet_preferences: Optional[Dict[str, Any]] = None,
                                      max_results: int = 5) -> List[Dict[str, Any]]:
        """Find products with similar nutritional values."""
        return self.products.find_similar_nutrition_products(
            product_id=product_id,
            diet_preferences=diet_preferences,
            max_results=max_results
        )

    def get_category_nutrition_analysis(
        self,
        category_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive nutrition analysis for a category.
        
        Returns:
            Dictionary containing:
            - statistics: Basic stats (min, max, avg, etc.)
            - distributions: Distribution of values for each nutrient
            - trends: Any notable trends in the data
        """
        # Get basic stats and distributions
        analysis = self.products.get_category_nutrition_stats(category_id)
        
        # Add trend analysis
        stats = analysis.get('statistics', {})
        trends = {}
        
        for nutrient, nutrient_stats in stats.items():
            if isinstance(nutrient_stats, dict):
                avg = nutrient_stats.get('avg', 0)
                std_dev = nutrient_stats.get('std_dev', 0)
                p50 = nutrient_stats.get('percentiles', {}).get('p50', 0)
                min_val = nutrient_stats.get('min', 0)
                max_val = nutrient_stats.get('max', 0)
                
                trends[nutrient] = {
                    'variability': 'high' if std_dev > avg * 0.5 else 'normal',
                    'skew': 'high' if avg > p50 else 'low',
                    'range': max_val - min_val,
                    'concentration': 'high' if max_val > avg * 2 else 'normal'
                }
        
        analysis['trends'] = trends
        return analysis
    
    # Stock Operations
    @transaction.atomic
    def update_product_stock(self, product_id: uuid.UUID, quantity_change: int) -> Product:
        """Update product stock with validation."""
        return self.products.update_stock(product_id, quantity_change)

    @transaction.atomic
    def bulk_update_product_prices(self, price_updates: List[Dict[str, Any]]) -> None:
        """Bulk update product prices."""
        return self.products.bulk_update_prices(price_updates)

    @transaction.atomic
    def update_product_availability(self, product_id: uuid.UUID, available: bool) -> Product:
        """Update product availability status."""
        product = self.products.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)
        
        return self.products.update_product(product, {'available': available})
