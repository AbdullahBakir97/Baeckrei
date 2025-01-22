from typing import Dict, Any, Optional, List
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.core.cache import cache
import logging
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..services.PMS import ProductManagementService
from ..pagination import StandardResultsSetPagination
from ..models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
from ..serializers import (
    ProductSerializer, CategorySerializer, 
    IngredientSerializer, AllergenInfoSerializer,
    ProductCreateUpdateSerializer, CategoryCreateUpdateSerializer,
    IngredientCreateUpdateSerializer, AllergenCreateUpdateSerializer,
    NutritionInfoCreateUpdateSerializer, NutritionDetailSerializer,
    NutritionAnalysisSerializer, SimilarProductSerializer,
    NutritionInfoSerializer, ProductDetailSerializer
)
from ..exceptions import EXCEPTIONS
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

logger = logging.getLogger(__name__)

class ProductManagementController(ViewSet):
    """
    Unified controller for managing products, categories, ingredients, and allergens.
    Provides a RESTful API interface to the ProductManagementService.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProductManagementService()
        self.paginator = StandardResultsSetPagination()
    
    def _handle_error(self, error: Exception) -> Response:
        """Handle different types of errors and return appropriate responses."""
        if isinstance(error, EXCEPTIONS.ValidationError):
            return Response(
                {
                    'error': error.message,
                    'code': error.code,
                    'field': error.field,
                    'reason': error.reason
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle duplicate errors
        if isinstance(error, (
            EXCEPTIONS.DuplicateProductError,
            EXCEPTIONS.DuplicateCategoryError,
            EXCEPTIONS.DuplicateIngredientError,
            EXCEPTIONS.DuplicateAllergenError
        )):
            return Response(
                {
                    'error': error.message,
                    'code': error.code
                },
                status=status.HTTP_409_CONFLICT
            )
            
        # Handle not found errors
        if isinstance(error, (
            EXCEPTIONS.ProductNotFoundError,
            EXCEPTIONS.CategoryNotFoundError,
            EXCEPTIONS.IngredientNotFoundError,
            EXCEPTIONS.AllergenNotFoundError
        )):
            return Response(
                {
                    'error': error.message,
                    'code': error.code
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Handle stock-related errors
        if isinstance(error, (EXCEPTIONS.InsufficientStockError, EXCEPTIONS.NegativeStockError)):
            return Response(
                {
                    'error': error.message,
                    'code': error.code,
                    'product_id': error.product_id,
                    'available_stock': getattr(error, 'available_stock', None),
                    'required_quantity': getattr(error, 'required_quantity', None)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Handle pricing errors
        if isinstance(error, (EXCEPTIONS.PricingError, EXCEPTIONS.NegativePriceError)):
            return Response(
                {
                    'error': error.message,
                    'code': error.code,
                    'product_id': error.product_id,
                    'price': error.price
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Handle resource in use errors
        if isinstance(error, (EXCEPTIONS.CategoryInUseError, EXCEPTIONS.IngredientInUseError)):
            return Response(
                {
                    'error': error.message,
                    'code': error.code,
                    'product_count': error.product_count
                },
                status=status.HTTP_409_CONFLICT
            )
            
        # Handle any other product management errors
        if isinstance(error, EXCEPTIONS.ProductError):
            return Response(
                {
                    'error': error.message,
                    'code': error.code
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        return Response(
            {
                'error': 'An unexpected error occurred. Please try again later.',
                'code': 'INTERNAL_SERVER_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def _paginate_response(self, queryset, request):
        """Helper method to paginate queryset and return response."""
        page = self.paginator.paginate_queryset(queryset, request)
        if page is not None:
            return self.paginator.get_paginated_response(page)
        return Response(queryset)
    
    def _apply_filters(self, queryset, request):
        """Helper method to apply filters and search."""
        filter_backend = DjangoFilterBackend()
        search_backend = filters.SearchFilter()
        
        if hasattr(self, 'filter_class'):
            queryset = filter_backend.filter_queryset(request, queryset, self)
        if hasattr(self, 'search_fields'):
            queryset = search_backend.filter_queryset(request, queryset, self)
            
        return queryset
    
    # Product Operations
    def list(self, request: Request) -> Response:
        """List products with optional filtering."""
        try:
            # Extract filter parameters
            category_ids = request.query_params.getlist('category_ids', None)
            price_range = {
                'min': request.query_params.get('min_price'),
                'max': request.query_params.get('max_price')
            } if 'min_price' in request.query_params or 'max_price' in request.query_params else None
            dietary_prefs = {
                'is_vegetarian': request.query_params.get('is_vegetarian'),
                'is_vegan': request.query_params.get('is_vegan'),
                'is_gluten_free': request.query_params.get('is_gluten_free')
            } if any(key in request.query_params for key in ['is_vegetarian', 'is_vegan', 'is_gluten_free']) else None
            allergen_exclusions = request.query_params.getlist('exclude_allergens', None)
            search_query = request.query_params.get('search', None)
            
            products = self.service.get_filtered_products(
                category_ids=category_ids,
                price_range=price_range,
                dietary_prefs=dietary_prefs,
                allergen_exclusions=allergen_exclusions,
                search_query=search_query
            )
            
            products = self._apply_filters(products, request)
            
            # Log the first product for debugging
            if products:
                first_product = products.first()
                print(f"Debug - First product: ID={first_product.id}, Image={first_product.image.url if first_product.image else None}")
            
            # Serialize with request context
            serializer = ProductSerializer(
                products, 
                many=True,
                context={'request': request}
            )
            
            return self._paginate_response(serializer.data, request)
        except Exception as e:
            print(f"Error in product list: {str(e)}")
            return self._handle_error(e)
    
    def retrieve(self, request: Request, pk=None) -> Response:
        """Retrieve a product by ID."""
        try:
            # Get product with all related data
            product = Product.objects.select_related(
                'category',
                'nutrition_info'
            ).prefetch_related(
                'ingredients',
                'ingredients__allergens'  # Only prefetch nested allergens
            ).get(pk=pk)
            
            # Log product data for debugging
            logger.debug(f"Retrieved product details:")
            logger.debug(f"- ID: {product.id}")
            logger.debug(f"- Name: {product.name}")
            logger.debug(f"- Category: {product.category.name if product.category else 'None'}")
            logger.debug(f"- Price: {product.price}")
            logger.debug(f"- Stock: {product.stock}")
            
            # Safely log image URL
            try:
                image_url = product.image.url if product.image else None
                logger.debug(f"- Image: {image_url}")
            except Exception as img_error:
                logger.warning(f"Error accessing image URL: {str(img_error)}")
                image_url = None
            
            logger.debug(f"- Ingredients: {list(product.ingredients.values_list('name', flat=True))}")
            
            # Serialize with request context for absolute URLs
            serializer = ProductDetailSerializer(
                product,
                context={'request': request}
            )
            
            return Response(serializer.data)
            
        except Product.DoesNotExist:
            return Response(
                {'message': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving product: {str(e)}", exc_info=True)
            return Response(
                {'message': f'Failed to retrieve product: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request: Request) -> Response:
        """Create a new product with relations."""
        try:
            serializer = ProductCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            product = self.service.create_product_with_relations(serializer.validated_data)
            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._handle_error(e)
    
    def update(self, request: Request, pk=None) -> Response:
        """Update a product and its relations."""
        try:
            serializer = ProductCreateUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            product = self.service.update_product_with_relations(pk, serializer.validated_data)
            return Response(ProductSerializer(product).data)
        except Exception as e:
            return self._handle_error(e)
    
    def destroy(self, request: Request, pk=None) -> Response:
        """Delete a product."""
        try:
            self.service.delete_product(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
    
    # Category Operations
    @action(detail=False, methods=['get'])
    def categories(self, request: Request) -> Response:
        """List all categories with their products."""
        try:
            categories = self.service.categories.get_queryset().filter(is_active=True)
            categories = self._apply_filters(categories, request)
            serialized_data = CategorySerializer(categories, many=True).data
            return self._paginate_response(serialized_data, request)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['get'])
    def category_summary(self, request: Request, pk=None) -> Response:
        """Get category summary with products and allergens."""
        try:
            summary = self.service.get_category_products_summary(pk)
            if not summary:
                return Response(
                    {'error': 'Category not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'category': CategorySerializer(summary['category']).data,
                'products_count': summary['products_count'],
                'active_products': ProductSerializer(summary['active_products'], many=True).data,
                'common_allergens': AllergenInfoSerializer(summary['common_allergens'], many=True).data
            })
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['post'])
    def create_category(self, request: Request) -> Response:
        """Create a new category."""
        try:
            serializer = CategoryCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            category = self.service.create_category(serializer.validated_data)
            return Response(
                CategorySerializer(category).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['put'])
    def update_category(self, request: Request, pk=None) -> Response:
        """Update a category."""
        try:
            serializer = CategoryCreateUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            category = self.service.update_category(pk, serializer.validated_data)
            return Response(CategorySerializer(category).data)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['delete'])
    def delete_category(self, request: Request, pk=None) -> Response:
        """Delete a category."""
        try:
            self.service.delete_category(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
    
    # Ingredient Operations
    @action(detail=False, methods=['get'])
    def ingredients(self, request: Request) -> Response:
        """List all ingredients with their allergens."""
        try:
            ingredients = self.service.products.ingredient_service.get_queryset().filter(active=True)
            ingredients = self._apply_filters(ingredients, request)
            serialized_data = IngredientSerializer(ingredients, many=True).data
            return self._paginate_response(serialized_data, request)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['get'])
    def ingredient_details(self, request: Request, pk=None) -> Response:
        """Get detailed ingredient information."""
        try:
            details = self.service.get_ingredient_details(pk)
            if not details:
                return Response(
                    {'error': 'Ingredient not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'ingredient': IngredientSerializer(details['ingredient']).data,
                'allergens': AllergenInfoSerializer(details['allergens'], many=True).data,
                'usage_count': details['usage_count'],
                'products': ProductSerializer(details['products'], many=True).data
            })
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['post'])
    def create_ingredient(self, request: Request) -> Response:
        """Create a new ingredient."""
        try:
            serializer = IngredientCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            ingredient = self.service.create_ingredient(serializer.validated_data)
            return Response(
                IngredientSerializer(ingredient).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['put'])
    def update_ingredient(self, request: Request, pk=None) -> Response:
        """Update an ingredient."""
        try:
            serializer = IngredientCreateUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            ingredient = self.service.update_ingredient(pk, serializer.validated_data)
            return Response(IngredientSerializer(ingredient).data)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['delete'])
    def delete_ingredient(self, request: Request, pk=None) -> Response:
        """Delete an ingredient."""
        try:
            self.service.delete_ingredient(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
    
    # Allergen Operations
    @action(detail=False, methods=['get'])
    def allergens(self, request: Request) -> Response:
        """List all allergens with their usage information."""
        try:
            allergens = self.service.products.ingredient_service.get_allergen_queryset()
            allergens = self._apply_filters(allergens, request)
            serialized_data = AllergenInfoSerializer(allergens, many=True).data
            return self._paginate_response(serialized_data, request)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['get'])
    def allergen_usage(self, request: Request, pk=None) -> Response:
        """Get allergen usage information."""
        try:
            usage = self.service.get_allergen_usage(pk)
            if not usage:
                return Response(
                    {'error': 'Allergen not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'allergen': AllergenInfoSerializer(usage['allergen']).data,
                'ingredients': IngredientSerializer(usage['ingredients'], many=True).data,
                'product_count': usage['product_count'],
                'ingredient_count': usage['ingredient_count']
            })
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['post'])
    def create_allergen(self, request: Request) -> Response:
        """Create a new allergen."""
        try:
            serializer = AllergenCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            allergen = self.service.create_allergen(serializer.validated_data)
            return Response(
                AllergenInfoSerializer(allergen).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['put'])
    def update_allergen(self, request: Request, pk=None) -> Response:
        """Update an allergen."""
        try:
            serializer = AllergenCreateUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            allergen = self.service.update_allergen(pk, serializer.validated_data)
            return Response(AllergenInfoSerializer(allergen).data)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=True, methods=['delete'])
    def delete_allergen(self, request: Request, pk=None) -> Response:
        """Delete an allergen."""
        try:
            self.service.delete_allergen(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
    
    # Additional Category Operations
    @action(detail=False, methods=['post'])
    def update_category_order(self, request: Request) -> Response:
        """Update the display order of categories."""
        try:
            self.service.update_category_order(request.data)
            return Response({'message': 'Category order updated successfully'})
        except Exception as e:
            return self._handle_error(e)
    
    # Additional Product Operations
    @action(detail=True, methods=['get'])
    def product_allergens(self, request: Request, pk=None) -> Response:
        """Get all allergens associated with a product through its ingredients."""
        try:
            allergens = self.service.get_product_allergens(pk)
            return Response(AllergenInfoSerializer(allergens, many=True).data)
        except Exception as e:
            return self._handle_error(e)
    
    # Additional Category Operations
    @action(detail=True, methods=['get'])
    def category_allergens(self, request: Request, pk=None) -> Response:
        """Get all allergens associated with products in a category."""
        try:
            allergens = self.service.get_category_allergens(pk)
            return Response(AllergenInfoSerializer(allergens, many=True).data)
        except Exception as e:
            return self._handle_error(e)
    
    # Bulk Operations
    @action(detail=False, methods=['post'])
    def bulk_update_products(self, request: Request) -> Response:
        """Bulk update products."""
        try:
            self.service.bulk_update_products(request.data)
            return Response({'message': 'Products updated successfully'})
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['post'])
    def bulk_update_stock(self, request: Request) -> Response:
        """Bulk update product stock levels."""
        try:
            self.service.bulk_update_stock(request.data)
            return Response({'message': 'Stock levels updated successfully'})
        except Exception as e:
            return self._handle_error(e)
    
    # Search Operations
    @action(detail=False, methods=['get'])
    def search(self, request: Request) -> Response:
        """Search across all entities."""
        try:
            query = request.query_params.get('q', '')
            results = self.service.search_all(query)
            
            return Response({
                'products': ProductSerializer(results['products'], many=True).data,
                'categories': CategorySerializer(results['categories'], many=True).data,
                'ingredients': IngredientSerializer(results['ingredients'], many=True).data,
                'allergens': AllergenInfoSerializer(results['allergens'], many=True).data
            })
        except Exception as e:
            return self._handle_error(e)
    
    # Reporting Operations
    @action(detail=False, methods=['get'])
    def report(self, request: Request) -> Response:
        """Generate a comprehensive report."""
        try:
            report_type = request.query_params.get('type', 'complete')
            report = self.service.generate_report(report_type=report_type)
            return Response(report)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['get'])
    def inventory_report(self, request: Request) -> Response:
        """Generate a comprehensive inventory report with insights."""
        try:
            cache_key = "inventory_report"
            report = cache.get(cache_key)
            
            if not report:
                report = self.service.generate_report(report_type='inventory')
                cache.set(cache_key, report, timeout=300)  # 5 minutes
            
            return Response(report)
        except Exception as e:
            return self._handle_error(e)
    
    # Nutrition Operations
    @action(detail=True, methods=['get'])
    def product_nutrition(self, request: Request, pk=None) -> Response:
        """Get comprehensive nutrition information for a product."""
        try:
            weight_grams = request.query_params.get('weight_grams')
            diet_type = request.query_params.get('diet_type')

            # Convert weight to Decimal if provided
            if weight_grams:
                weight_grams = Decimal(weight_grams)

            nutrition = self.service.get_product_nutrition(
                product_id=pk,
                weight_grams=weight_grams,
                diet_type=diet_type
            )
            serializer = NutritionDetailSerializer(nutrition)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)

    @action(detail=True, methods=['post'])
    def update_nutrition(self, request: Request, pk=None) -> Response:
        """Add or update nutrition information for a product."""
        try:
            serializer = NutritionInfoCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            weight_grams = serializer.validated_data.pop('weight_grams', None)
            product = self.service.add_product_nutrition(
                product_id=pk,
                nutrition_data=serializer.validated_data,
                weight_grams=weight_grams
            )
            return Response(ProductSerializer(product).data)
        except Exception as e:
            return self._handle_error(e)

    @action(detail=True, methods=['get'])
    def similar_nutrition_products(self, request: Request, pk=None) -> Response:
        """Find products with similar nutritional values."""
        try:
            diet_preferences = request.query_params.get('diet_preferences', {})
            max_results = int(request.query_params.get('max_results', 5))

            similar = self.service.find_similar_nutrition_products(
                product_id=pk,
                diet_preferences=diet_preferences,
                max_results=max_results
            )
            serializer = SimilarProductSerializer(similar, many=True)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)

    @action(detail=True, methods=['get'])
    def category_nutrition(self, request: Request, pk=None) -> Response:
        """Get comprehensive nutrition analysis for a category."""
        try:
            analysis = self.service.get_category_nutrition_analysis(category_id=pk)
            serializer = NutritionAnalysisSerializer(analysis)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)

    @action(detail=True, methods=['get'])
    def related_products(self, request: Request, pk=None) -> Response:
        """Get related products based on category and attributes."""
        try:
            product = Product.objects.get(pk=pk)
            
            # Get products from the same category
            related = Product.objects.filter(
                category=product.category,
                status='active',
                available=True
            ).exclude(pk=pk)
            
            # Add products with similar attributes
            if not related.exists():
                related = Product.objects.filter(
                    Q(is_vegan=product.is_vegan) |
                    Q(is_vegetarian=product.is_vegetarian) |
                    Q(is_gluten_free=product.is_gluten_free),
                    status='active',
                    available=True
                ).exclude(pk=pk)
            
            # Limit to 4 products
            related = related[:4]
            
            serializer = ProductSerializer(related, many=True)
            return Response(serializer.data)
            
        except Product.DoesNotExist:
            return Response(
                {'message': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self._handle_error(e)
