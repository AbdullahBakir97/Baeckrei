"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configure Swagger documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Baeckrei API",
      default_version='v1',
      description="API documentation for Baeckrei e-commerce platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@baeckrei.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Configure API URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/shopping-cart/', include('apps.cart.urls', namespace='cart')),
    path('api/orders/', include('apps.orders.urls')),
    
    # API Documentation (using drf-yasg)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Add static and media URLs in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)