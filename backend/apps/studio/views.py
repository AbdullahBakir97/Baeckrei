"""The admin's API ("Backlover Studio"): everything the bakery manages that
is not orders, products, categories or users. Staff only."""
import csv
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.content.models import ContactMessage, NewsletterCampaign, NewsletterSubscriber, Post
from apps.menuboard.models import MenuScreen, MenuSlide
from apps.menuboard.serializers import ScreenSerializer, SlideSerializer
from apps.products.models import AllergenInfo, Ingredient, NutritionInfo, Product
from apps.shop import config as shop_config
from apps.shop.models import ClosingDay, ShopSettings

from .serializers import (
    AllergenSerializer, CampaignSerializer, ClosingDaySerializer, ContactMessageSerializer, IngredientSerializer,
    NutritionSerializer, PostSerializer, ProductRecipeSerializer, ReplySerializer, ShopSettingsSerializer,
    SubscriberSerializer,
)

logger = logging.getLogger(__name__)
UPLOADS = [MultiPartParser, FormParser, JSONParser]


def _paragraphs(text):
    return [p.strip() for p in (text or '').replace('\r\n', '\n').split('\n\n') if p.strip()]


def _email_context(**extra):
    shop = shop_config.get()
    return {'shop_name': shop.name, 'shop_address': shop_config.address_line(shop), **extra}


class StaffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]


# ---- Overview ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAdminUser])
def summary(request):
    """Counts for the sidebar badges and the dashboard."""
    now = timezone.now()
    return Response({
        'unread_messages': ContactMessage.objects.filter(handled=False).count(),
        'subscribers': NewsletterSubscriber.objects.filter(unsubscribed_at__isnull=True).count(),
        'scheduled_posts': Post.objects.filter(published_at__gt=now).count(),
        'draft_posts': Post.objects.filter(published_at__isnull=True).count(),
        'screens': MenuScreen.objects.count(),
        'screens_online': sum(1 for s in MenuScreen.objects.only('last_seen_at') if s.online),
    })


# ---- Shop settings --------------------------------------------------------------

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def shop_settings(request):
    """The saved settings plus the values in effect (saved or server default)."""
    row = ShopSettings.load()
    if request.method != 'GET':
        serializer = ShopSettingsSerializer(row, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        row = serializer.save()
    effective = shop_config.get()
    hours = effective.opening_hours
    return Response({
        'saved': ShopSettingsSerializer(row).data,
        'effective': {
            **{key: getattr(effective, key) for key in (
                'name', 'street', 'city', 'notification_email', 'pickup_lead_minutes', 'delivery_lead_minutes',
                'slot_minutes', 'slot_days', 'slot_capacity')},
            'delivery_fee': str(effective.delivery_fee),
            'opening_hours': {str(day): [[o.strftime('%H:%M'), c.strftime('%H:%M')] for o, c in hours.get(day, [])]
                              for day in range(7)},
        },
    })


class ClosingDayViewSet(StaffViewSet):
    serializer_class = ClosingDaySerializer

    def get_queryset(self):
        days = ClosingDay.objects.all()
        if self.request.query_params.get('upcoming') == 'true':
            today = timezone.localdate()
            days = days.filter(Q(end__gte=today) | Q(end__isnull=True, start__gte=today))
        return days


# ---- Journal ----------------------------------------------------------------------

class PostViewSet(StaffViewSet):
    serializer_class = PostSerializer
    parser_classes = UPLOADS

    def get_queryset(self):
        posts = Post.objects.select_related('author').order_by('-created_at')
        now = timezone.now()
        state = self.request.query_params.get('state')
        if state == 'draft':
            posts = posts.filter(published_at__isnull=True)
        elif state == 'scheduled':
            posts = posts.filter(published_at__gt=now)
        elif state == 'published':
            posts = posts.filter(published_at__lte=now)
        search = self.request.query_params.get('search')
        if search:
            posts = posts.filter(Q(title__icontains=search) | Q(body__icontains=search))
        return posts

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ---- Contact messages -------------------------------------------------------------

class MessageViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ContactMessageSerializer

    def get_queryset(self):
        messages = ContactMessage.objects.select_related('replied_by')
        state = self.request.query_params.get('state')
        if state == 'open':
            messages = messages.filter(handled=False)
        elif state == 'done':
            messages = messages.filter(handled=True)
        search = self.request.query_params.get('search')
        if search:
            messages = messages.filter(Q(name__icontains=search) | Q(email__icontains=search)
                                       | Q(subject__icontains=search) | Q(message__icontains=search))
        return messages

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Email an answer to the sender and file the message as done."""
        message = self.get_object()
        serializer = ReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['reply']
        context = _email_context(message=message, paragraphs=_paragraphs(text))
        subject = f"Re: {message.subject or context['shop_name']}"
        email = EmailMultiAlternatives(subject, render_to_string('studio/email/reply.txt', context),
                                       settings.DEFAULT_FROM_EMAIL, [message.email])
        email.attach_alternative(render_to_string('studio/email/reply.html', context), 'text/html')
        notify = shop_config.get().notification_email
        if notify:
            email.reply_to = [notify]
        try:
            email.send()
        except Exception:
            logger.exception('Could not send the reply to contact message %s', message.pk)
            return Response({'detail': 'The email could not be sent. Check the email settings.'},
                            status=status.HTTP_502_BAD_GATEWAY)
        message.reply, message.replied_at, message.replied_by, message.handled = text, timezone.now(), request.user, True
        message.save(update_fields=['reply', 'replied_at', 'replied_by', 'handled'])
        return Response(ContactMessageSerializer(message).data)


# ---- Newsletter ---------------------------------------------------------------------

class SubscriberViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SubscriberSerializer

    def get_queryset(self):
        people = NewsletterSubscriber.objects.all()
        state = self.request.query_params.get('state')
        if state == 'active':
            people = people.filter(unsubscribed_at__isnull=True)
        elif state == 'unsubscribed':
            people = people.filter(unsubscribed_at__isnull=False)
        search = self.request.query_params.get('search')
        if search:
            people = people.filter(email__icontains=search)
        return people

    def perform_create(self, serializer):
        serializer.save(email=serializer.validated_data['email'].lower())

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        person = self.get_object()
        if not person.unsubscribed_at:
            person.unsubscribed_at = timezone.now()
            person.save(update_fields=['unsubscribed_at'])
        return Response(SubscriberSerializer(person).data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Active subscribers as CSV, e.g. for a newsletter service."""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="newsletter-subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['email', 'subscribed_at'])
        for person in NewsletterSubscriber.objects.filter(unsubscribed_at__isnull=True).order_by('subscribed_at'):
            writer.writerow([person.email, timezone.localtime(person.subscribed_at).strftime('%Y-%m-%d %H:%M')])
        return response


def _newsletter_message(campaign, to, token, connection=None):
    base = settings.FRONTEND_URL.rstrip('/')
    unsubscribe_url = f'{base}/newsletter/unsubscribe?token={token}'
    context = _email_context(subject=campaign.subject, paragraphs=_paragraphs(campaign.body),
                             unsubscribe_url=unsubscribe_url, shop_url=f'{base}/products')
    email = EmailMultiAlternatives(campaign.subject, render_to_string('studio/email/newsletter.txt', context),
                                   settings.DEFAULT_FROM_EMAIL, [to], connection=connection,
                                   headers={'List-Unsubscribe': f'<{unsubscribe_url}>'})
    email.attach_alternative(render_to_string('studio/email/newsletter.html', context), 'text/html')
    return email


class CampaignViewSet(StaffViewSet):
    serializer_class = CampaignSerializer
    queryset = NewsletterCampaign.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().sent_at:
            raise ValidationError('A sent newsletter stays in the history.')
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send the newsletter to the signed-in admin only."""
        campaign = self.get_object()
        to = request.data.get('email') or request.user.email
        try:
            _newsletter_message(campaign, to, 'test').send()
        except Exception:
            logger.exception('Could not send the test newsletter %s', campaign.pk)
            return Response({'detail': 'The email could not be sent. Check the email settings.'},
                            status=status.HTTP_502_BAD_GATEWAY)
        return Response({'sent_to': to})

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send to every active subscriber, each with their own unsubscribe link."""
        with transaction.atomic():
            campaign = NewsletterCampaign.objects.select_for_update().get(pk=self.get_object().pk)
            if campaign.sent_at:
                raise ValidationError('This newsletter was already sent.')
            campaign.sent_at = timezone.now()
            campaign.save(update_fields=['sent_at'])
        people = list(NewsletterSubscriber.objects.filter(unsubscribed_at__isnull=True))
        sent = 0
        connection = get_connection()
        try:
            connection.open()
            for person in people:
                try:
                    _newsletter_message(campaign, person.email, person.token, connection).send()
                    sent += 1
                except Exception:
                    logger.exception('Newsletter %s: could not send to %s', campaign.pk, person.pk)
        finally:
            connection.close()
        campaign.recipient_count = sent
        campaign.save(update_fields=['recipient_count'])
        return Response(CampaignSerializer(campaign).data)


# ---- Ingredients, allergens, nutrition ------------------------------------------------------

class AllergenViewSet(StaffViewSet):
    serializer_class = AllergenSerializer
    queryset = AllergenInfo.objects.all().order_by('name')

    def destroy(self, request, *args, **kwargs):
        allergen = self.get_object()
        if allergen.ingredients.exists():
            raise ValidationError('Remove this allergen from its ingredients first.')
        allergen.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(StaffViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        items = Ingredient.objects.prefetch_related('allergens').order_by('name')
        search = self.request.query_params.get('search')
        return items.filter(name__icontains=search) if search else items

    def destroy(self, request, *args, **kwargs):
        ingredient = self.get_object()
        if ingredient.products.exists():
            raise ValidationError('This ingredient is used in products. Remove it there first.')
        ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def product_recipe(request, pk):
    """A product's ingredients and nutrition values per 100 g."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'PUT':
        serializer = ProductRecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            product.ingredients.set(serializer.validated_data['ingredients'])
            nutrition = serializer.validated_data.get('nutrition')
            if nutrition:
                if product.nutrition_info_id:
                    NutritionInfo.objects.filter(pk=product.nutrition_info_id).update(**nutrition)
                else:
                    product.nutrition_info = NutritionInfo.objects.create(**nutrition)
                    product.save(update_fields=['nutrition_info'])
            elif 'nutrition' in request.data and product.nutrition_info_id:
                old = product.nutrition_info
                product.nutrition_info = None
                product.save(update_fields=['nutrition_info'])
                old.delete()
        product.refresh_from_db()
    allergens = AllergenInfo.objects.filter(ingredients__products=product).distinct().order_by('name')
    return Response({
        'ingredients': [i.pk for i in product.ingredients.all()],
        'nutrition': NutritionSerializer(product.nutrition_info).data if product.nutrition_info else None,
        'allergens': [a.name for a in allergens],
    })


# ---- Menu screens --------------------------------------------------------------------------

class ScreenViewSet(StaffViewSet):
    serializer_class = ScreenSerializer
    parser_classes = UPLOADS
    queryset = MenuScreen.objects.all()

    @action(detail=True, methods=['post'])
    def reload(self, request, pk=None):
        """The screen reloads itself within a minute."""
        screen = self.get_object()
        MenuScreen.objects.filter(pk=screen.pk).update(reload_token=screen.reload_token + 1)
        screen.refresh_from_db()
        return Response(self.get_serializer(screen).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        slides = list(original.slides.all())
        copy = MenuScreen.objects.get(pk=original.pk)
        copy.pk, copy.slug, copy.code, copy.is_default = None, '', '', False
        copy.name = f'{original.name} (2)'
        copy.last_seen_at, copy.last_seen_info, copy.reload_token = None, {}, 0
        copy.save()
        for slide in slides:
            slide.pk, slide.screen = None, copy
            slide.save()
        return Response(self.get_serializer(copy).data, status=status.HTTP_201_CREATED)


class SlideViewSet(StaffViewSet):
    serializer_class = SlideSerializer
    parser_classes = UPLOADS

    def get_queryset(self):
        slides = MenuSlide.objects.select_related('product')
        screen = self.request.query_params.get('screen')
        return slides.filter(screen_id=screen) if screen else slides
