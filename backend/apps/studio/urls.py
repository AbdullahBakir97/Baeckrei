from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('closing-days', views.ClosingDayViewSet, basename='studio-closing-day')
router.register('posts', views.PostViewSet, basename='studio-post')
router.register('messages', views.MessageViewSet, basename='studio-message')
router.register('subscribers', views.SubscriberViewSet, basename='studio-subscriber')
router.register('campaigns', views.CampaignViewSet, basename='studio-campaign')
router.register('allergens', views.AllergenViewSet, basename='studio-allergen')
router.register('ingredients', views.IngredientViewSet, basename='studio-ingredient')
router.register('menu-screens', views.ScreenViewSet, basename='studio-menu-screen')
router.register('menu-slides', views.SlideViewSet, basename='studio-menu-slide')

urlpatterns = [
    path('summary/', views.summary, name='studio-summary'),
    path('settings/', views.shop_settings, name='studio-settings'),
    path('products/<uuid:pk>/recipe/', views.product_recipe, name='studio-product-recipe'),
    path('', include(router.urls)),
]
