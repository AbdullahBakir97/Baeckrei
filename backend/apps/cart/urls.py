from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CartViewSet

app_name = 'cart'

# Define URL patterns for cart operations
urlpatterns = [
    # Get current cart
    path('', CartViewSet.as_view({'get': 'current'}), name='cart-detail'),
    
    # Add item to cart
    path('add_item/', CartViewSet.as_view({'post': 'add_item'}), name='add-to-cart'),
    
    # Remove item from cart
    path('remove/<uuid:product_id>/', 
         CartViewSet.as_view({'delete': 'remove_item'}), 
         name='remove-from-cart'),
    
    # Update cart item
    path('update/<uuid:product_id>/', 
         CartViewSet.as_view({'put': 'update_item'}), 
         name='update-cart-item'),
    
    # Clear cart
    path('clear/', CartViewSet.as_view({'post': 'clear'}), name='clear-cart'),
]

# Format suffix patterns without registering the converter
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
