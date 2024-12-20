from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    IngredientSerializer,
    AllergenInfoSerializer
)
from .models import Product, Category, Ingredient, AllergenInfo
from .controllers.product_controller import ProductController
from .controllers.category_controller import CategoryController
from .controllers.ingredient_controller import IngredientController
from .controllers.allergen_controller import AllergenController
from .services.reports import ReportService
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductPagination(StandardResultsSetPagination):
    page_size = 12  # Better for grid layouts (3x4, 4x3, etc.)


class CategoryPagination(StandardResultsSetPagination):
    page_size = 20


class IngredientPagination(StandardResultsSetPagination):
    page_size = 15


class AllergenPagination(StandardResultsSetPagination):
    page_size = 15


class ReportsView(APIView):
    """View for accessing various reports."""
    
    def get(self, request, report_type=None):
        try:
            if report_type == 'products':
                return Response(ReportService.get_product_statistics())
            elif report_type == 'categories':
                return Response(ReportService.get_category_statistics())
            elif report_type == 'ingredients':
                return Response(ReportService.get_ingredient_statistics())
            elif report_type == 'allergens':
                return Response(ReportService.get_allergen_statistics())
            elif report_type == 'inventory':
                return Response(ReportService.generate_inventory_report())
            else:
                return Response({
                    'products': ReportService.get_product_statistics(),
                    'categories': ReportService.get_category_statistics(),
                    'ingredients': ReportService.get_ingredient_statistics(),
                    'allergens': ReportService.get_allergen_statistics(),
                    'inventory': ReportService.generate_inventory_report()
                })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories."""
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = CategoryController()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.controller.get_category_list(self.request.query_params)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            category = self.controller.create_category(serializer.validated_data)
            response_serializer = self.get_serializer(category)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        try:
            category = self.controller.update_category(instance.id, serializer.validated_data)
            response_serializer = self.get_serializer(category)
            return Response(response_serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.controller.delete_category(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder categories."""
        try:
            self.controller.reorder_categories(request.data)
            return Response(status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, slug=None):
        """Toggle category active status."""
        instance = self.get_object()
        try:
            category = self.controller.toggle_category_status(instance.id)
            serializer = self.get_serializer(category)
            return Response(serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def statistics(self, request):
        """Get category statistics."""
        try:
            stats = self.controller.get_category_statistics()
            return Response(stats)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products."""
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'category': ['exact'],
        'price': ['gte', 'lte'],
        'is_vegan': ['exact'],
        'is_vegetarian': ['exact'],
        'is_gluten_free': ['exact'],
        'available': ['exact'],
    }
    search_fields = ['name', 'description', 'category__name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ProductController()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'featured']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        return Product.objects.all().select_related('category')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = self.controller.create_product(serializer.validated_data)
            response_serializer = self.get_serializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        try:
            product = self.controller.update_product(instance.id, serializer.validated_data)
            response_serializer = self.get_serializer(product)
            return Response(response_serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.controller.delete_product(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def featured(self, request):
        """Get featured products."""
        featured_products = Product.objects.filter(is_featured=True)[:4]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle product availability."""
        try:
            product = self.controller.toggle_product_availability(pk)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock."""
        try:
            quantity_change = int(request.data.get('quantity_change', 0))
            product = self.controller.update_product_stock(pk, quantity_change)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False, methods=['post'])
    def bulk_update_prices(self, request):
        """Bulk update product prices."""
        try:
            self.controller.bulk_update_prices(request.data)
            return Response(status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def statistics(self, request):
        """Get product statistics."""
        try:
            stats = self.controller.generate_product_report()
            return Response(stats)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ingredients."""
    serializer_class = IngredientSerializer
    pagination_class = IngredientPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = IngredientController()
    
    def get_queryset(self):
        return self.controller.get_ingredient_list(self.request.query_params)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ingredient = self.controller.create_ingredient(serializer.validated_data)
            response_serializer = self.get_serializer(ingredient)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        try:
            ingredient = self.controller.update_ingredient(instance.id, serializer.validated_data)
            response_serializer = self.get_serializer(ingredient)
            return Response(response_serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.controller.delete_ingredient(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle ingredient active status."""
        try:
            ingredient = self.controller.toggle_ingredient_status(pk)
            serializer = self.get_serializer(ingredient)
            return Response(serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def commonly_used(self, request):
        """Get commonly used ingredients."""
        limit = int(request.query_params.get('limit', 10))
        ingredients = self.controller.get_commonly_used_ingredients(limit)
        serializer = self.get_serializer(ingredients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update_allergens(self, request):
        """Bulk update ingredient allergens."""
        try:
            self.controller.bulk_update_allergens(request.data)
            return Response(status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def statistics(self, request):
        """Get ingredient statistics."""
        try:
            stats = self.controller.get_ingredient_statistics()
            return Response(stats)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))


class AllergenViewSet(viewsets.ModelViewSet):
    """ViewSet for managing allergens."""
    serializer_class = AllergenInfoSerializer
    pagination_class = AllergenPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = AllergenController()
    
    def get_queryset(self):
        return self.controller.get_allergen_list(self.request.query_params)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            allergen = self.controller.create_allergen(serializer.validated_data)
            response_serializer = self.get_serializer(allergen)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        try:
            allergen = self.controller.update_allergen(instance.id, serializer.validated_data)
            response_serializer = self.get_serializer(allergen)
            return Response(response_serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.controller.delete_allergen(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def most_common(self, request):
        """Get most common allergens."""
        limit = int(request.query_params.get('limit', 10))
        allergens = self.controller.get_most_common_allergens(limit)
        serializer = self.get_serializer(allergens, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def by_category(self, request):
        """Get allergens by category."""
        category_id = request.query_params.get('category_id')
        if not category_id:
            raise ValidationError(detail="category_id is required")
        allergens = self.controller.get_allergens_by_category(category_id)
        serializer = self.get_serializer(allergens, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def merge(self, request):
        """Merge allergens."""
        source_id = request.data.get('source_id')
        target_id = request.data.get('target_id')
        if not source_id or not target_id:
            raise ValidationError(detail="Both source_id and target_id are required")
        try:
            allergen = self.controller.merge_allergens(source_id, target_id)
            serializer = self.get_serializer(allergen)
            return Response(serializer.data)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
    
    @action(detail=False)
    def statistics(self, request):
        """Get allergen statistics."""
        try:
            stats = self.controller.get_allergen_statistics()
            return Response(stats)
        except DjangoValidationError as e:
            raise ValidationError(detail=str(e))
