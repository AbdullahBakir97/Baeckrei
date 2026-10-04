from rest_framework import serializers

from .models import ContactMessage, Post


class ContactMessageSerializer(serializers.ModelSerializer):
    # Hidden field that people never fill in; bots usually do.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message', 'website')


class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'title_en', 'slug', 'excerpt', 'excerpt_en', 'cover_image', 'author_name', 'published_at')

    def get_author_name(self, obj):
        if not obj.author:
            return ''
        return ' '.join(filter(None, [obj.author.first_name, obj.author.last_name])) or ''


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('body', 'body_en', 'updated_at')
