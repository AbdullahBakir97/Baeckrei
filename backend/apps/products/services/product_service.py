from functools import cache
from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet, F, Q, Sum, Avg, Count, Min, Max
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
from ..models import Product, NutritionInfo
from .base import BaseService
from .. import EXCEPTIONS
from .ingredient_allergen_service import IngredientAllergenService
from .nutrition_service import NutritionService
import uuid
from decimal import Decimal

class ProductService(BaseService[Product]):
    """Service class for Product-related operations with business logic."""
    
    # Cache keys
    PRODUCT_CACHE_KEY = 'product:{}'
    ALL_PRODUCTS_CACHE_KEY = 'all_products'
    CACHE_TIMEOUT = getattr(settings, 'PRODUCT_CACHE_TIMEOUT', 3600)  # 1 hour default

    def __init__(self):
        super().__init__(Product)
        self.ingredient_service = IngredientAllergenService()
        self.nutrition_service = NutritionService()
    
    def get_queryset(self) -> QuerySet[Product]:
        """Get the base queryset with related fields."""
        return Product.objects.with_related()
    
    def get_available_products(self, 
                             category_ids: Optional[List[uuid.UUID]] = None,
                             price_range: Optional[Dict[str, float]] = None,
                             dietary_prefs: Optional[Dict[str, bool]] = None,
                             search_query: Optional[str] = None,
                             ordering: Optional[List[str]] = None) -> QuerySet[Product]:
        """
        Get available products with multiple filter options.
        
        Args:
            category_ids: Optional list of category UUIDs to filter by
            price_range: Optional dict with 'min' and 'max' price values
            dietary_prefs: Optional dict with dietary preference flags
            search_query: Optional search string for product name/description
            ordering: Optional list of fields to order by
            
        Returns:
            Filtered and ordered queryset of products
        """
        try:
            # Build filters dictionary
            filters = {
                'available_only': True,  # Always filter available products
                'category_ids': category_ids or [],
                'min_price': price_range.get('min') if price_range else None,
                'max_price': price_range.get('max') if price_range else None
            }
            
            # Add dietary preferences if provided
            if dietary_prefs:
                filters.update({
                    'is_vegan': dietary_prefs.get('vegan', False),
                    'is_vegetarian': dietary_prefs.get('vegetarian', False),
                    'is_gluten_free': dietary_prefs.get('gluten_free', False)
                })
            
            return Product.objects.filter_products(
                filters=filters,
                search_query=search_query,
                ordering=ordering
            )
            
        except EXCEPTIONS.ValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error filtering products: {str(e)}",
                code="PRODUCT_FILTER_ERROR"
            )

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
        return self.get_queryset().related_products(product_id, limit)
    
    def get_featured_products(self, limit: int = 6) -> QuerySet[Product]:
        """Get featured products."""
        return Product.objects.featured(limit=limit)
    
    def get_products_by_allergens(self, exclude_allergens: List[uuid.UUID]) -> QuerySet[Product]:
        """Get products excluding specific allergens."""
        return Product.objects.available().by_allergen(exclude_allergens)
    
    @transaction.atomic
    def update_stock(self, product_id: uuid.UUID, quantity_change: int) -> Product:
        """Update product stock with validation."""
        # Get product with stock status
        product = Product.objects.with_related().with_stock_status().get(id=product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(
                product_id=product_id,
                message=f"Product not found"
            )
        
        # Prevent negative stock
        if quantity_change < 0 and product.stock + quantity_change < 0:
            raise EXCEPTIONS.InsufficientStockError(
                product_id=product_id,
                required_quantity=abs(quantity_change),
                available_stock=product.stock,
                message=(
                    f"Insufficient stock for product '{product.name}': "
                    f"Requested {abs(quantity_change)} units but only {product.stock} available"
                )
            )
        
        # Update stock and refresh from db
        new_stock = product.stock + quantity_change
        Product.objects.filter(id=product_id).update(
            stock=new_stock,
            available=new_stock > 0
        )
        return self.get_by_id(product_id)

    def get_product_statistics(self) -> Dict[str, Any]:
        """Get comprehensive product statistics."""
        queryset = self.with_related().with_stock_status()
        
        # Get basic counts and aggregates
        stats = {
            'total_products': queryset.count(),
            'active_products': queryset.filter(status='active').count(),
            'discontinued_products': queryset.filter(status='discontinued').count(),
            'low_stock_products': queryset.filter(is_low_stock=True).count(),
            'out_of_stock_products': queryset.filter(needs_restock=True).count(),
            'average_price': queryset.aggregate(Avg('price'))['price__avg'],
            'total_stock': queryset.aggregate(Sum('stock'))['stock__sum']
        }
        
        # Get category distribution
        stats['category_distribution'] = (
            queryset.values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Get price ranges
        price_stats = queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )
        stats['price_statistics'] = price_stats
        
        return stats
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate a comprehensive inventory report."""
        products = Product.objects.with_related().with_stock_status()
        
        report = {
            'low_stock_items': (
                products.filter(is_low_stock=True)
                .annotate(category_name=F('category__name'))
                .values('id', 'name', 'stock', 'min_stock', 'category_name', 'price')
            ),
            'out_of_stock': (
                products.filter(needs_restock=True)
                .annotate(category_name=F('category__name'))
                .values('id', 'name', 'category_name', 'price')
            ),
            'overstocked_items': (
                products.filter(stock__gt=F('max_stock'))
                .annotate(category_name=F('category__name'))
                .values('id', 'name', 'stock', 'max_stock', 'category_name', 'price')
            )
        }
        
        # Add stock value calculations
        stock_values = products.aggregate(
            total_value=Sum(F('price') * F('stock')),
            avg_item_value=Avg(F('price') * F('stock'))
        )
        report['stock_value'] = stock_values
        
        return report

    def get_by_id(self, product_id: Union[str, uuid.UUID]) -> Optional[Product]:
        """Get a product by its ID with all related data."""
        try:
            return Product.objects.with_related().get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get_by_category(self, category_ids: List[uuid.UUID]) -> QuerySet[Product]:
        """Get products by category IDs."""
        return Product.objects.with_related().by_category(category_ids)

    def get_by_price_range(self, min_price: float = None, max_price: float = None) -> QuerySet[Product]:
        """Get products within a price range."""
        return Product.objects.with_related().by_price_range(min_price, max_price)

    def search_products(self, query: str) -> QuerySet[Product]:
        """Search products by name, description, or category."""
        return Product.objects.with_related().search(query)

    def get_dietary_products(self, **preferences) -> QuerySet[Product]:
        """Get products filtered by dietary preferences."""
        return Product.objects.with_related().dietary_preferences(**preferences)

    def get_category_nutrition_stats(
        self,
        category_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get nutrition statistics for a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            Dictionary with nutrition statistics and distributions
        """
        # Get basic statistics
        stats = self.nutrition_service.get_nutrition_stats(category_id)
        
        # Add distribution for each nutrient
        distributions = {}
        for nutrient in ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']:
            distributions[nutrient] = self.nutrition_service.get_nutrition_distribution(
                nutrient,
                category_id
            )
            
        return {
            'statistics': stats,
            'distributions': distributions
        }

    @transaction.atomic
    def update_product(self, product: Product, data: Dict[str, Any]) -> Product:
        """Update an existing product's basic information."""
        # Check for duplicate name/SKU if being updated
        name = data.get('name')
        sku = data.get('sku')
        if name or sku:
            existing = Product.objects.filter(
                Q(name=name) | Q(sku=sku)
            ).exclude(id=product.id)
            if existing.exists():
                raise EXCEPTIONS.DuplicateProductError(
                    name=name,
                    sku=sku,
                    message=f"Cannot update product: Another product with name '{name}' or SKU '{sku}' already exists"
                )

        # Validate price if it's being updated
        price = data.get('price')
        if price is not None and price < 0:
            raise EXCEPTIONS.NegativePriceError(
                product_id=product.id,
                price=price,
                message=f"Cannot update product '{product.name}' with negative price: {price}"
            )

        try:
            updated_product = super().update(product, **data)
            self.invalidate_product_cache(product.id)
            return updated_product
        except EXCEPTIONS.ValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product: {str(e)}",
                code="PRODUCT_UPDATE_ERROR"
            )
    
    @transaction.atomic
    def bulk_update_prices(self, price_updates: List[Dict[str, Any]]) -> None:
        """
        Bulk update product prices.
        
        Args:
            price_updates: List of dictionaries containing product ID and new price
                         Each dict should have 'id' and 'price' keys
        """
        try:
            # Extract IDs and validate products exist
            product_ids = [update['id'] for update in price_updates]
            existing_products = set(
                Product.objects.filter(id__in=product_ids).values_list('id', flat=True)
            )
            
            # Check for missing products
            missing_ids = set(product_ids) - existing_products
            if missing_ids:
                raise EXCEPTIONS.ProductNotFoundError(
                    product_id=list(missing_ids)[0],
                    message=f"Products not found: {', '.join(str(id) for id in missing_ids)}"
                )
            
            # Validate prices
            invalid_prices = [
                update for update in price_updates
                if update['price'] < 0
            ]
            if invalid_prices:
                raise EXCEPTIONS.NegativePriceError(
                    price=invalid_prices[0]['price'],
                    message=f"Cannot update prices: Negative prices not allowed"
                )
            
            # Prepare updates
            products = []
            for update in price_updates:
                product = Product(id=update['id'])
                product.price = update['price']
                products.append(product)
            
            # Perform bulk update
            self.bulk_update(products, ['price'])
            
            # Invalidate cache for updated products
            for product_id in product_ids:
                self.invalidate_product_cache(product_id)
                
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.ProductNotFoundError,
                EXCEPTIONS.NegativePriceError):
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product prices: {str(e)}",
                code="PRODUCT_PRICE_UPDATE_ERROR"
            )
    
    def get_product(self, product_id: uuid.UUID) -> Optional[Product]:
        """
        Retrieve a product with caching.
        
        Args:
            product_id: UUID of the product to retrieve
            
        Returns:
            Product instance if found, None otherwise
        """
        cache_key = self.PRODUCT_CACHE_KEY.format(product_id)
        
        # Try to get from cache
        product = cache.get(cache_key)
        if product is not None:
            return product
            
        try:
            # Get from database with all related data
            product = self.get_by_id(product_id)
            if not product:
                # Cache negative lookup to prevent repeated DB queries
                cache.set(cache_key, None, timeout=300)  # 5 minutes for negative cache
                return None
            
            # Cache the result
            cache.set(cache_key, product, timeout=self.CACHE_TIMEOUT)
            return product
            
        except Product.DoesNotExist:
            # Cache negative lookup
            cache.set(cache_key, None, timeout=300)
            return None

    def get_all_products(self, force_refresh: bool = False) -> List[Product]:
        """
        Retrieve all products with caching.
        
        Args:
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            List of all products
        """
        if not force_refresh:
            # Try to get from cache
            products = cache.get(self.ALL_PRODUCTS_CACHE_KEY)
            if products is not None:
                return products
                
        # Get from database with all related data
        products = list(Product.objects.with_related())
        
        # Cache the result
        cache.set(self.ALL_PRODUCTS_CACHE_KEY, products, timeout=self.CACHE_TIMEOUT)
        return products

    def invalidate_product_cache(self, product_id: Optional[uuid.UUID] = None):
        """
        Invalidate product cache.
        
        Args:
            product_id: If provided, invalidate specific product cache,
                      otherwise invalidate all products cache
        """
        if product_id:
            cache_key = self.PRODUCT_CACHE_KEY.format(product_id)
            cache.delete(cache_key)
        
        # Always invalidate all products cache when any product changes
        cache.delete(self.ALL_PRODUCTS_CACHE_KEY)

    def delete_product(self, product: Product):
        """Delete a product and its associated nutrition info."""
        if product.nutrition_info:
            self.nutrition_service.delete_nutrition_info(product.nutrition_info.id)
        super().delete(product)
        self.invalidate_product_cache(product.id)

    @transaction.atomic
    def create_product_with_ingredients(self, data: Dict[str, Any]) -> Product:
        """
        Create a product and handle its ingredient relationships.
        
        Args:
            data: Product data including ingredients
            
        Returns:
            Created product instance
        """
        # Extract and remove ingredients data
        ingredient_data = data.pop('ingredients', [])
        
        # Create the product first
        product = self.create_product(data)
        
        # Handle ingredients and their allergens
        if ingredient_data:
            ingredient_ids = []
            for ing_data in ingredient_data:
                if 'id' in ing_data:
                    # Get existing ingredient
                    ingredient = self.ingredient_service.get_ingredient_by_id(ing_data['id'])
                    if not ingredient:
                        raise EXCEPTIONS.IngredientNotFoundError(
                            ingredient_id=ing_data['id']
                        )
                else:
                    # Create new ingredient with its allergens
                    ingredient = self.ingredient_service.create_ingredient_with_allergens(ing_data)
                ingredient_ids.append(ingredient.id)
            
            # Set ingredients for the product
            self.update_product_ingredients(product.id, ingredient_ids)
        
        return product

    @transaction.atomic
    def update_product_with_ingredients(self, product_id: uuid.UUID, data: Dict[str, Any]) -> Product:
        """
        Update a product and its ingredient relationships.
        
        Args:
            product_id: ID of the product to update
            data: Updated product data including optional ingredients
            
        Returns:
            Updated product instance
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            IngredientNotFoundError: If an ingredient ID is invalid
            AllergenNotFoundError: If an allergen ID is invalid
            ValidationError: If ingredient data is invalid
        """
        try:
            # Get product first to ensure it exists
            product = self.get_by_id(product_id)
            if not product:
                raise EXCEPTIONS.ProductNotFoundError(
                    product_id=product_id,
                    message=f"Cannot update product: Product with ID '{product_id}' not found"
                )
            
            # Extract and remove ingredients data if present
            ingredient_data = data.pop('ingredients', None)
            
            # Update product fields first
            updated_product = self.update_product(product, data)
            
            # Handle ingredients update if provided
            if ingredient_data is not None:
                ingredient_ids = []
                for ing_data in ingredient_data:
                    if not isinstance(ing_data, dict):
                        raise EXCEPTIONS.ValidationError(
                            field='ingredients',
                            value=ing_data,
                            reason='Each ingredient must be a dictionary'
                        )
                        
                    if 'id' in ing_data:
                        ingredient = self.ingredient_service.get_ingredient_by_id(ing_data['id'])
                        if not ingredient:
                            raise EXCEPTIONS.IngredientNotFoundError(
                                ingredient_id=ing_data['id']
                            )
                        ingredient_ids.append(ingredient.id)
                    else:
                        # Create new ingredient with allergens
                        ingredient = self.ingredient_service.create_ingredient_with_allergens(ing_data)
                        ingredient_ids.append(ingredient.id)
                
                # Update product's ingredients
                self.update_product_ingredients(product_id, ingredient_ids)
            
            return updated_product
            
        except (EXCEPTIONS.ValidationError, EXCEPTIONS.ProductNotFoundError,
                EXCEPTIONS.IngredientNotFoundError):
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product with ingredients: {str(e)}",
                code="PRODUCT_UPDATE_ERROR"
            )

    @transaction.atomic
    def update_product_ingredients(self, product_id: uuid.UUID, ingredient_ids: List[uuid.UUID]) -> Product:
        """
        Update product ingredients.
        
        Args:
            product_id: ID of the product to update
            ingredient_ids: List of ingredient IDs to set
            
        Returns:
            Updated product instance
            
        Raises:
            ProductNotFoundError: If product doesn't exist
        """
        product = self.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(
                product_id=product_id,
                message=f"Cannot update ingredients: Product with ID '{product_id}' not found"
            )
            
        try:
            # Validate all ingredients exist
            for ingredient_id in ingredient_ids:
                if not self.ingredient_service.get_ingredient_by_id(ingredient_id):
                    raise EXCEPTIONS.IngredientNotFoundError(
                        ingredient_id=ingredient_id,
                        message=f"Cannot update ingredients: Ingredient with ID '{ingredient_id}' not found"
                    )
            
            # Use set() to efficiently update the many-to-many relationship
            product.ingredients.set(ingredient_ids)
            
            # Invalidate cache since ingredients changed
            self.invalidate_product_cache(product_id)
            
            return product
            
        except EXCEPTIONS.IngredientNotFoundError:
            # Re-raise ingredient errors
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product ingredients: {str(e)}",
                code="PRODUCT_INGREDIENTS_UPDATE_ERROR"
            )

    @transaction.atomic
    def create_product(self, data: Dict[str, Any]) -> Product:
        """Create a new product with basic information."""
        # Validate required fields
        required_fields = ['name', 'price']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise EXCEPTIONS.ValidationError(
                field='required_fields',
                value=missing_fields,
                reason='Missing required fields for product creation',
                message=f"Cannot create product: Missing required fields: {', '.join(missing_fields)}"
            )

        # Validate price
        price = data.get('price')
        if price is not None and price < 0:
            raise EXCEPTIONS.NegativePriceError(
                price=price,
                message=f"Cannot create product with negative price: {price}"
            )

        # Check for duplicate name/SKU before creation
        name = data.get('name')
        sku = data.get('sku')
        if Product.objects.filter(Q(name=name) | Q(sku=sku)).exists():
            raise EXCEPTIONS.DuplicateProductError(
                name=name,
                sku=sku,
                message=f"Cannot create product: A product with name '{name}' or SKU '{sku}' already exists"
            )

        try:
            product = super().create(**data)
            self.invalidate_product_cache()
            return product
        except EXCEPTIONS.ValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error creating product: {str(e)}",
                code="PRODUCT_CREATE_ERROR"
            )

    @transaction.atomic
    def create_product_with_nutrition(self, data: Dict[str, Any]) -> Product:
        """
        Create a product with nutrition information.
        
        Args:
            data: Dictionary containing both product and nutrition data
                 The nutrition data should be under the 'nutrition_info' key
        """
        # Extract nutrition data
        nutrition_data = data.pop('nutrition_info', None)
        if not nutrition_data:
            raise EXCEPTIONS.ValidationError(
                field='nutrition_info',
                value=None,
                reason='Nutrition information is required',
                message="Cannot create product: Nutrition information is required"
            )

        # Validate nutrition data
        NutritionInfo.validate_nutrition_data(nutrition_data)

        # Create the product first
        product = self.create_product(data)
        
        try:
            # Add nutrition information
            self.add_product_nutrition(product.id, nutrition_data)
            return product
        except Exception as e:
            # Clean up the product if nutrition creation fails
            self.delete_product(product)
            raise

    @transaction.atomic
    def add_product_nutrition(
        self,
        product_id: uuid.UUID,
        nutrition_data: Dict[str, Any],
        weight_grams: Optional[Decimal] = None
    ) -> Product:
        """
        Add or update nutrition information for a product.
        
        Args:
            product_id: Product ID
            nutrition_data: Nutrition data to add
            weight_grams: Optional weight in grams. If provided, nutrition_data
                         should be for this weight and will be converted to per 100g
        """
        product = self.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)

        # If weight provided, convert nutrition values to per 100g
        if weight_grams:
            multiplier = Decimal('100') / weight_grams
            nutrition_data = {
                k: v * multiplier
                for k, v in nutrition_data.items()
                if k in NutritionInfo.REQUIRED_FIELDS
            }

        # Create or update nutrition info
        try:
            if product.nutrition_info:
                nutrition = self.nutrition_service.update_nutrition_info(
                    product.nutrition_info.id,
                    nutrition_data
                )
            else:
                nutrition = self.nutrition_service.create_nutrition_info(nutrition_data)
                product.nutrition_info = nutrition
                product.save()

            return product

        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Failed to add nutrition info: {str(e)}",
                code="PRODUCT_NUTRITION_ERROR"
            )

    @transaction.atomic
    def update_product_nutrition(self, product_id: uuid.UUID, nutrition_data: Dict[str, Any]) -> Product:
        """
        Update a product's nutrition information.
        
        Args:
            product_id: ID of the product to update
            nutrition_data: New nutrition information data
            
        Returns:
            Updated product instance
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            NutritionValidationError: If nutrition data is invalid
        """
        product = self.get_by_id(product_id)
        if not product:
            raise EXCEPTIONS.ProductNotFoundError(product_id=product_id)

        # Validate nutrition data
        NutritionInfo.validate_nutrition_data(nutrition_data)
            
        try:
            if product.nutrition_info:
                # Update existing nutrition info
                self.nutrition_service.update_nutrition_info(
                    product.nutrition_info.id,
                    nutrition_data
                )
            else:
                # Create new nutrition info
                nutrition_info = self.nutrition_service.create_nutrition_info(nutrition_data)
                product.nutrition_info = nutrition_info
                product.save()
            return product
        except EXCEPTIONS.NutritionValidationError:
            raise
        except Exception as e:
            raise EXCEPTIONS.ProductError(
                message=f"Error updating product nutrition info: {str(e)}",
                code="PRODUCT_NUTRITION_ERROR"
            )

    def get_product_nutrition(
        self,
        product_id: uuid.UUID,
        weight_grams: Optional[Decimal] = None,
        diet_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive nutrition information for a product.
        
        Args:
            product_id: Product ID
            weight_grams: Optional specific weight to calculate for
            diet_type: Optional diet type for daily value calculation
            
        Returns:
            Dictionary containing:
            - nutrition_values: Base nutrition values
            - daily_percentages: Percentage of daily values
            - weight_based: Nutrition for specific weight if provided
        """
        product = self.get_by_id(product_id)
        if not product or not product.nutrition_info:
            raise EXCEPTIONS.ProductError(
                message="Product not found or has no nutrition info",
                code="PRODUCT_NUTRITION_NOT_FOUND"
            )

        return self.nutrition_service.get_comprehensive_info(
            nutrition_id=product.nutrition_info.id,
            weight_grams=weight_grams,
            diet_type=diet_type
        )

    def find_similar_nutrition_products(
        self,
        product_id: uuid.UUID,
        diet_preferences: Optional[Dict[str, Any]] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find products with similar nutritional values.
        
        Args:
            product_id: Source product ID
            diet_preferences: Optional diet preferences
            max_results: Maximum number of results to return
            
        Returns:
            List of similar products with similarity scores
        """
        product = self.get_by_id(product_id)
        if not product or not product.nutrition_info:
            raise EXCEPTIONS.ProductError(
                message="Product not found or has no nutrition info",
                code="PRODUCT_NUTRITION_NOT_FOUND"
            )

        return self.nutrition_service.find_similar_products(
            nutrition_id=product.nutrition_info.id,
            diet_preferences=diet_preferences,
            max_results=max_results
        )

    def get_products_by_ingredient(self, ingredient_id: uuid.UUID) -> QuerySet[Product]:
        """Get all products containing a specific ingredient."""
        return self.with_related().by_ingredient(ingredient_id)
