from django.urls import path

from . import views

urlpatterns = [
    path('pair/<str:code>/', views.pair, name='menu-screen-pair'),
    path('<slug:slug>/board/', views.board, name='menu-screen-board'),
    path('<slug:slug>/heartbeat/', views.heartbeat, name='menu-screen-heartbeat'),
]
