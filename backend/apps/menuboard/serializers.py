from rest_framework import serializers

from .models import MenuScreen, MenuSlide

DESIGN_FIELDS = (
    'name', 'slug', 'layout', 'theme', 'font', 'background_color', 'text_color', 'accent_color',
    'background_image_url', 'background_dim', 'orientation', 'language', 'headline', 'headline_en',
    'headline_ar', 'ticker', 'ticker_en', 'ticker_ar', 'show_prices', 'show_descriptions', 'show_images', 'show_tags', 'show_qr',
    'show_clock', 'show_status', 'sold_out', 'page_seconds', 'slide_every', 'reload_token',
)


def _absolute(request, field):
    if not field:
        return None
    return request.build_absolute_uri(field.url) if request else field.url


class PublicScreenSerializer(serializers.ModelSerializer):
    """What a screen needs to draw itself (no device or admin details)."""
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = MenuScreen
        fields = DESIGN_FIELDS

    def get_background_image_url(self, obj):
        return _absolute(self.context.get('request'), obj.background_image)


class PublicSlideSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MenuSlide
        fields = ('id', 'style', 'title', 'title_en', 'title_ar', 'text', 'text_en', 'text_ar', 'price', 'price_note',
                  'price_note_en', 'price_note_ar', 'image_url', 'seconds')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return _absolute(request, obj.image)
        if obj.product and obj.product.image:
            return _absolute(request, obj.product.image)
        return None


class ScreenSerializer(serializers.ModelSerializer):
    """The admin's view of a screen."""
    background_image_url = serializers.SerializerMethodField()
    online = serializers.BooleanField(read_only=True)
    slide_count = serializers.SerializerMethodField()
    remove_background_image = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = MenuScreen
        fields = ('id', 'code', 'is_default', 'categories', 'featured_products', 'hidden_products',
                  'background_image', 'remove_background_image', 'last_seen_at', 'last_seen_info', 'online',
                  'slide_count', 'created_at', 'updated_at') + DESIGN_FIELDS
        read_only_fields = ('code', 'slug', 'reload_token', 'last_seen_at', 'last_seen_info', 'created_at', 'updated_at')
        extra_kwargs = {'background_image': {'write_only': True, 'required': False}}

    def get_background_image_url(self, obj):
        return _absolute(self.context.get('request'), obj.background_image)

    def get_slide_count(self, obj):
        return obj.slides.count() if obj.pk else 0

    def validate(self, attrs):
        for key in ('background_color', 'text_color', 'accent_color'):
            value = attrs.get(key)
            if value and not (len(value) == 7 and value.startswith('#')):
                raise serializers.ValidationError({key: 'Use a colour like #e6a15a.'})
        for key in ('categories', 'featured_products', 'hidden_products'):
            if key in attrs and not isinstance(attrs[key], list):
                raise serializers.ValidationError({key: 'Expected a list.'})
        return attrs

    def update(self, instance, validated_data):
        if validated_data.pop('remove_background_image', False):
            instance.background_image.delete(save=False)
            instance.background_image = None
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('remove_background_image', None)
        return super().create(validated_data)


class SlideSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    remove_image = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = MenuSlide
        fields = ('id', 'screen', 'style', 'title', 'title_en', 'title_ar', 'text', 'text_en', 'text_ar', 'price',
                  'price_note', 'price_note_en', 'price_note_ar', 'image', 'image_url', 'remove_image', 'product', 'active', 'order', 'seconds', 'start_date', 'end_date',
                  'start_time', 'end_time', 'weekdays')
        extra_kwargs = {'image': {'write_only': True, 'required': False}}

    def get_image_url(self, obj):
        return PublicSlideSerializer(obj, context=self.context).data['image_url']

    def validate_weekdays(self, value):
        if not isinstance(value, list) or any(not isinstance(d, int) or not 0 <= d <= 6 for d in value):
            raise serializers.ValidationError('Use weekday numbers 0 (Monday) to 6 (Sunday).')
        return sorted(set(value))

    def update(self, instance, validated_data):
        if validated_data.pop('remove_image', False):
            instance.image.delete(save=False)
            instance.image = None
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('remove_image', None)
        return super().create(validated_data)
