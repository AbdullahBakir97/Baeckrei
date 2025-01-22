from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ViewSet

from .controllers.PMC import ProductManagementController
from .serializers import (
    ProductSerializer, ProductListSerializer, ProductDetailSerializer,
    CategorySerializer, IngredientSerializer, AllergenInfoSerializer,
    NutritionDetailSerializer, NutritionAnalysisSerializer,
    SimilarProductSerializer
)


class ProductManagementViewSet(ViewSet):
    """
    Unified ViewSet for managing products, categories, ingredients, allergens, and nutrition.
    Provides a comprehensive API interface through ProductManagementController.
    """
    search_fields = ['name', 'description']
    filter_fields = ['category', 'is_active', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = ProductManagementController()

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

    # Product Operations
    def list(self, request):
        return self.controller.list(request)

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
