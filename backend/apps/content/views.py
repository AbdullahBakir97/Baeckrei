import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import NewsletterSubscriber, Post
from .serializers import (
    ContactMessageSerializer,
    NewsletterSubscribeSerializer,
    NewsletterUnsubscribeSerializer,
    PostDetailSerializer,
    PostListSerializer,
)

logger = logging.getLogger(__name__)


class ContactMessageView(APIView):
    """Store a contact form message and notify the shop by email."""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.pop('website', ''):
            # Honeypot filled in: pretend it worked, store nothing.
            return Response({'message': 'Thanks! We will get back to you soon.'}, status=status.HTTP_201_CREATED)
        message = serializer.save()
        if settings.SHOP_NOTIFICATION_EMAIL:
            try:
                send_mail(
                    subject=f'Contact form: {message.subject or message.name}',
                    message=f'From: {message.name} <{message.email}>\n\n{message.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.SHOP_NOTIFICATION_EMAIL],
                )
            except Exception:
                # The message is saved and visible in the admin either way.
                logger.exception('Could not send contact notification email')
        return Response({'message': 'Thanks! We will get back to you soon.'}, status=status.HTTP_201_CREATED)


class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'newsletter'

    def post(self, request):
        serializer = NewsletterSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created and subscriber.unsubscribed_at:
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=['unsubscribed_at'])
        # Same answer whether or not the address was already subscribed.
        return Response({'message': "You're subscribed. Thanks!"}, status=status.HTTP_201_CREATED)


class NewsletterUnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NewsletterUnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = NewsletterSubscriber.objects.filter(
            token=serializer.validated_data['token'], unsubscribed_at__isnull=True
        ).update(unsubscribed_at=timezone.now())
        exists = updated or NewsletterSubscriber.objects.filter(token=serializer.validated_data['token']).exists()
        if not exists:
            return Response({'detail': 'This unsubscribe link is not valid.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': "You've been unsubscribed from the newsletter."})


class PostListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostListSerializer

    def get_queryset(self):
        return Post.objects.published().select_related('author')


class PostDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.published().select_related('author')
