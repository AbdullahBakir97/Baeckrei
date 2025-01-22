from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductManagementViewSet

router = DefaultRouter()
router.register(r'', ProductManagementViewSet, basename='products')

app_name = 'products'

# The router automatically generates URLs for:
# List/Create: /api/products/
# Retrieve/Update/Delete: /api/products/{id}/
# Categories: /api/products/categories/
# Category operations: /api/products/{id}/category_summary/
# Ingredients: /api/products/ingredients/
# Ingredient operations: /api/products/{id}/ingredient_details/
# Allergens: /api/products/allergens/
# Allergen operations: /api/products/{id}/allergen_usage/
# Nutrition: /api/products/{id}/product_nutrition/
# Reports: /api/products/report/, /api/products/inventory_report/
# Search: /api/products/search/

urlpatterns = [
    path('', include(router.urls)),
]
