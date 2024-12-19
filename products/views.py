from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
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

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories."""
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = CategoryController()
    
    def get_queryset(self):
        return self.controller.get_active_categories()

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing products."""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'category__slug': ['exact'],
        'price': ['gte', 'lte'],
        'is_vegan': ['exact'],
        'is_vegetarian': ['exact'],
        'is_gluten_free': ['exact'],
        'available': ['exact'],
    }
    search_fields = ['name', 'description', 'ingredients__name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ProductController()
    
    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == 'retrieve' else ProductListSerializer
    
    def get_queryset(self):
        return self.controller.get_product_list(
            filters=self.request.query_params
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.controller.create_product(serializer.validated_data)
        response_serializer = self.get_serializer(product)
        return Response(response_serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = self.controller.update_product(instance.id, serializer.validated_data)
        response_serializer = self.get_serializer(product)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.controller.delete_product(instance.id)
        return Response(status=204)
    
    @action(detail=False)
    def featured(self, request):
        """Return featured products."""
        products = self.controller.get_featured_products()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle product availability."""
        product = self.controller.toggle_product_availability(pk)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing ingredients."""
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = IngredientController()
    
    def get_queryset(self):
        return self.controller.get_ingredient_list(
            filters=self.request.query_params
        )

class AllergenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllergenInfo.objects.all()
    serializer_class = AllergenInfoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = AllergenController()
    
    def get_queryset(self):
        return self.controller.get_allergen_list(
            filters=self.request.query_params
        )
