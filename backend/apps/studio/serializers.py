from rest_framework import serializers

from apps.content.models import ContactMessage, NewsletterCampaign, NewsletterSubscriber, Post
from apps.products.models import AllergenInfo, Ingredient, NutritionInfo
from apps.shop.config import parse_weekly_hours
from apps.shop.models import ClosingDay, ShopSettings


class ShopSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopSettings
        exclude = ('id',)
        read_only_fields = ('updated_at',)

    def validate_opening_hours(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Expected {"0": [["07:00", "18:00"]], ...}.')
        try:
            parsed = parse_weekly_hours(value)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError(str(exc))
        # Store in a normal form: every weekday, ranges sorted.
        return {str(day): [[o.strftime('%H:%M'), c.strftime('%H:%M')] for o, c in parsed.get(day, [])] for day in range(7)}

    def validate(self, attrs):
        for key in ('slot_minutes', 'slot_days'):
            if attrs.get(key) == 0:
                raise serializers.ValidationError({key: 'Must be at least 1.'})
        return attrs


class ClosingDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosingDay
        fields = ('id', 'start', 'end', 'label', 'label_en')

    def validate(self, attrs):
        start = attrs.get('start', getattr(self.instance, 'start', None))
        end = attrs.get('end', getattr(self.instance, 'end', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end': 'The last day is before the first.'})
        return attrs


class PostSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    remove_cover_image = serializers.BooleanField(write_only=True, required=False)
    author_name = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'title_en', 'slug', 'excerpt', 'excerpt_en', 'body', 'body_en', 'cover_image',
                  'cover_image_url', 'remove_cover_image', 'author_name', 'published_at', 'state', 'created_at',
                  'updated_at')
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {'cover_image': {'write_only': True, 'required': False}, 'slug': {'required': False}}

    def get_cover_image_url(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url

    def get_author_name(self, obj):
        if not obj.author:
            return ''
        return ' '.join(filter(None, [obj.author.first_name, obj.author.last_name])) or obj.author.email

    def get_state(self, obj):
        from django.utils import timezone
        if not obj.published_at:
            return 'draft'
        return 'scheduled' if obj.published_at > timezone.now() else 'published'

    def validate_slug(self, value):
        from django.utils.text import slugify
        value = slugify(value)
        if value and Post.objects.filter(slug=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('Another post already uses this address.')
        return value

    def update(self, instance, validated_data):
        if validated_data.pop('remove_cover_image', False):
            instance.cover_image.delete(save=False)
            instance.cover_image = None
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('remove_cover_image', None)
        return super().create(validated_data)


class ContactMessageSerializer(serializers.ModelSerializer):
    replied_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'subject', 'message', 'created_at', 'handled', 'reply', 'replied_at',
                  'replied_by_name')
        read_only_fields = ('name', 'email', 'subject', 'message', 'created_at', 'reply', 'replied_at')

    def get_replied_by_name(self, obj):
        user = obj.replied_by
        return (' '.join(filter(None, [user.first_name, user.last_name])) or user.email) if user else ''


class ReplySerializer(serializers.Serializer):
    reply = serializers.CharField(max_length=10000)


class SubscriberSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = NewsletterSubscriber
        fields = ('id', 'email', 'subscribed_at', 'unsubscribed_at', 'active')
        read_only_fields = ('subscribed_at', 'unsubscribed_at')


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterCampaign
        fields = ('id', 'subject', 'body', 'created_at', 'updated_at', 'sent_at', 'recipient_count')
        read_only_fields = ('created_at', 'updated_at', 'sent_at', 'recipient_count')

    def validate(self, attrs):
        if self.instance and self.instance.sent_at:
            raise serializers.ValidationError('This newsletter was already sent.')
        return attrs


class AllergenSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.SerializerMethodField()

    class Meta:
        model = AllergenInfo
        fields = ('id', 'name', 'description', 'ingredient_count')

    def get_ingredient_count(self, obj):
        return obj.ingredients.count()

    def validate_name(self, value):
        if AllergenInfo.objects.filter(name__iexact=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('This allergen already exists.')
        return value


class IngredientSerializer(serializers.ModelSerializer):
    allergens = serializers.PrimaryKeyRelatedField(many=True, queryset=AllergenInfo.objects.all(), required=False)
    allergen_names = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'description', 'allergens', 'allergen_names', 'is_active', 'product_count')

    def get_allergen_names(self, obj):
        return [a.name for a in obj.allergens.all()]

    def get_product_count(self, obj):
        return obj.products.count()

    def validate_name(self, value):
        if Ingredient.objects.filter(name__iexact=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('This ingredient already exists.')
        return value


class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        fields = ('calories', 'proteins', 'carbohydrates', 'fats', 'fiber')


class ProductRecipeSerializer(serializers.Serializer):
    """Ingredients and nutrition of one product, edited with the product."""
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    nutrition = NutritionSerializer(allow_null=True, required=False)
