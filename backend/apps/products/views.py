from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ViewSet
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from apps.products.controllers.PMC import ProductManagementController
from apps.products.serializers import (
    ProductSerializer, ProductListSerializer, ProductDetailSerializer,
    CategorySerializer, IngredientSerializer, AllergenInfoSerializer,
    NutritionDetailSerializer, NutritionAnalysisSerializer,
    SimilarProductSerializer
)
from apps.products.models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
from apps.products.filters import ProductFilter, CategoryFilter, IngredientFilter
from apps.products.pagination import ProductPagination
from apps.products.exceptions import EXCEPTIONS
import logging

logger = logging.getLogger(__name__)

class ProductManagementViewSet(ViewSet):
    """
    Unified ViewSet for managing products, categories, ingredients, allergens, and nutrition.
    Provides a comprehensive API interface through ProductManagementController.
    """
    search_fields = ['name', 'description']
    filter_fields = ['category', 'available', 'price']
    pagination_class = ProductPagination
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    default_ordering = 'name'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ProductManagementController()
        self.pagination = self.pagination_class()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        public_actions = [
            'list', 'retrieve', 'categories', 'ingredients', 'allergens',
            'product_nutrition', 'similar_products', 'category_nutrition',
            'product_allergens', 'category_allergens', 'search', 'report',
            'inventory_report', 'related_products'
        ]
        if self.action in public_actions:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer based on the action.
        """
        serializer_mapping = {
            'list': ProductListSerializer,
            'retrieve': ProductDetailSerializer,
            'categories': CategorySerializer,
            'ingredients': IngredientSerializer,
            'allergens': AllergenInfoSerializer,
            'product_nutrition': NutritionDetailSerializer,
            'similar_products': SimilarProductSerializer,
            'category_nutrition': NutritionAnalysisSerializer,
        }
        return serializer_mapping.get(self.action, ProductSerializer)

    def handle_exception(self, exc):
        """
        Handle custom exceptions and convert them to DRF responses.
        """
        if isinstance(exc, EXCEPTIONS.ProductError):
            return Response(
                {"error": str(exc), "code": exc.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def _apply_ordering(self, queryset, request):
        """Apply ordering to queryset based on request parameters."""
        ordering = request.query_params.get('ordering', self.default_ordering)
        if ordering:
            if ordering.startswith('-'):
                field = ordering[1:]
            else:
                field = ordering
                
            if field not in self.ordering_fields:
                raise EXCEPTIONS.InvalidOrderingError(field=field)
                
            queryset = queryset.order_by(ordering)
        return queryset

    # Product Operations
    def list(self, request):
        """List products with filtering and pagination."""
        try:
            # Get base queryset with optimized prefetching
            queryset = Product.objects.select_related(
                'category', 
                'nutrition_info'
            ).prefetch_related(
                'ingredients',
                'ingredients__allergens'
            ).filter(
                available=True,
                category__is_active=True
            )
            
            # Add debug logging for initial query
            logger.debug(f"Total products in database: {Product.objects.count()}")
            logger.debug(f"Products with status='active': {Product.objects.filter(status='active').count()}")
            logger.debug(f"Available products: {Product.objects.filter(available=True).count()}")
            logger.debug(f"Products with active categories: {Product.objects.filter(category__is_active=True).count()}")
            logger.debug(f"Initial queryset count: {queryset.count()}")
            
            # Apply filters
            try:
                product_filter = ProductFilter(queryset)
                queryset = product_filter.apply_filters(request.query_params)
                logger.debug(f"After filters count: {queryset.count()}")
            except EXCEPTIONS.FilterError as e:
                logger.error(f"Filter error: {str(e)}")
                return Response(
                    {"error": str(e), "code": e.code},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Unexpected filter error: {str(e)}")
                return Response(
                    {"error": "Invalid filter parameters", "detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Apply ordering
            try:
                queryset = self._apply_ordering(queryset, request)
            except EXCEPTIONS.InvalidOrderingError as e:
                logger.error(f"Ordering error: {str(e)}")
                return Response(
                    {"error": str(e), "code": e.code},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Apply pagination
            try:
                page = self.pagination.paginate_queryset(queryset, request)
                if page is not None:
                    serializer = self.get_serializer_class()(page, many=True, context={'request': request})
                    return self.pagination.get_paginated_response(serializer.data)
                
                serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Pagination error: {str(e)}")
                return Response(
                    {"error": "Error applying pagination", "detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Unhandled error in product list: {str(e)}")
            return Response(
                {"error": "Internal server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        return self.controller.retrieve(request, pk)

    def create(self, request):
        return self.controller.create(request)

    def update(self, request, pk=None):
        return self.controller.update(request, pk)

    def destroy(self, request, pk=None):
        return self.controller.destroy(request, pk)

    # Category Operations
    @action(detail=False, methods=['get'])
    def categories(self, request):
        return self.controller.categories(request)

    @action(detail=True, methods=['get'])
    def category_summary(self, request, pk=None):
        return self.controller.category_summary(request, pk)

    @action(detail=False, methods=['post'])
    def create_category(self, request):
        return self.controller.create_category(request)

    @action(detail=True, methods=['put'])
    def update_category(self, request, pk=None):
        return self.controller.update_category(request, pk)

    @action(detail=True, methods=['delete'])
    def delete_category(self, request, pk=None):
        return self.controller.delete_category(request, pk)

    # Ingredient Operations
    @action(detail=False, methods=['get'])
    def ingredients(self, request):
        return self.controller.ingredients(request)

    @action(detail=True, methods=['get'])
    def ingredient_details(self, request, pk=None):
        return self.controller.ingredient_details(request, pk)

    @action(detail=False, methods=['post'])
    def create_ingredient(self, request):
        return self.controller.create_ingredient(request)

    @action(detail=True, methods=['put'])
    def update_ingredient(self, request, pk=None):
        return self.controller.update_ingredient(request, pk)

    @action(detail=True, methods=['delete'])
    def delete_ingredient(self, request, pk=None):
        return self.controller.delete_ingredient(request, pk)

    # Allergen Operations
    @action(detail=False, methods=['get'])
    def allergens(self, request):
        return self.controller.allergens(request)

    @action(detail=True, methods=['get'])
    def allergen_usage(self, request, pk=None):
        return self.controller.allergen_usage(request, pk)

    @action(detail=False, methods=['post'])
    def create_allergen(self, request):
        return self.controller.create_allergen(request)

    @action(detail=True, methods=['put'])
    def update_allergen(self, request, pk=None):
        return self.controller.update_allergen(request, pk)

    @action(detail=True, methods=['delete'])
    def delete_allergen(self, request, pk=None):
        return self.controller.delete_allergen(request, pk)

    # Nutrition Operations
    @action(detail=True, methods=['get'])
    def product_nutrition(self, request, pk=None):
        return self.controller.product_nutrition(request, pk)

    @action(detail=True, methods=['post'])
    def update_nutrition(self, request, pk=None):
        return self.controller.update_nutrition(request, pk)

    @action(detail=True, methods=['get'])
    def similar_products(self, request, pk=None):
        return self.controller.similar_products(request, pk)

    @action(detail=True, methods=['get'])
    def category_nutrition(self, request, pk=None):
        return self.controller.category_nutrition(request, pk)

    # Additional Operations
    @action(detail=False, methods=['post'])
    def update_category_order(self, request):
        return self.controller.update_category_order(request)

    @action(detail=True, methods=['get'])
    def product_allergens(self, request, pk=None):
        return self.controller.product_allergens(request, pk)

    @action(detail=True, methods=['get'])
    def category_allergens(self, request, pk=None):
        return self.controller.category_allergens(request, pk)

    @action(detail=False, methods=['post'])
    def bulk_update_products(self, request):
        return self.controller.bulk_update_products(request)

    @action(detail=False, methods=['post'])
    def bulk_update_stock(self, request):
        return self.controller.bulk_update_stock(request)

    @action(detail=False, methods=['get'])
    def search(self, request):
        return self.controller.search(request)

    @action(detail=False, methods=['get'])
    def report(self, request):
        return self.controller.report(request)

    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        return self.controller.inventory_report(request)

    @action(detail=True, methods=['get'])
    def related_products(self, request, pk=None):
        """Get related products for a specific product."""
        return self.controller.related_products(request, pk)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def dashboard_stats(self, request):
        """Get dashboard statistics."""
        try:
            total_products = Product.objects.count()
            low_stock_threshold = 10
            low_stock_count = Product.objects.filter(stock__lte=low_stock_threshold).count()
            
            return Response({
                'total_products': total_products,
                'low_stock_count': low_stock_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def low_stock(self, request):
        """Get products with low stock."""
        try:
            low_stock_threshold = 10
            low_stock_products = Product.objects.filter(
                stock__lte=low_stock_threshold,
                is_active=True
            ).order_by('stock')[:5]
            
            products_data = [{
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'price': str(product.price)
            } for product in low_stock_products]
            
            return Response(products_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
