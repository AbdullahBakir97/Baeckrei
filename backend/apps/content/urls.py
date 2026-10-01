from django.urls import path

from .views import (
    ContactMessageView,
    NewsletterSubscribeView,
    NewsletterUnsubscribeView,
    PostDetailView,
    PostListView,
)

urlpatterns = [
    path('contact/', ContactMessageView.as_view(), name='contact'),
    path('newsletter/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
]
