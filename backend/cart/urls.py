from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register('', CartViewSet, basename='cart')

# Add custom action URLs
urlpatterns = [
    path('current/', CartViewSet.as_view({'get': 'current'}), name='cart-current'),
    path('add_item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('remove_item/', CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('update_item/', CartViewSet.as_view({'post': 'update_item'}), name='cart-update-item'),
    path('clear/', CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
] + router.urls
