from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, opening_hours, stripe_webhook

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('payments/stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('opening-hours/', opening_hours, name='opening-hours'),
    path('', include(router.urls)),
]