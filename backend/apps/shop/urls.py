from django.urls import path

from . import views

urlpatterns = [
    path('info/', views.info, name='shop-info'),
]
