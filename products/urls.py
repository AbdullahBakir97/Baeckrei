from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('products', views.ProductViewSet, basename='product')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')
router.register('allergens', views.AllergenViewSet, basename='allergen')

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
    path('reports/', views.ReportsView.as_view(), name='reports-all'),
    path('reports/<str:report_type>/', views.ReportsView.as_view(), name='reports-specific'),
]
