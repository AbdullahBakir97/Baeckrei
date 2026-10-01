from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import ContactMessage, NewsletterSubscriber, Post


class ContactTests(TestCase):
    @override_settings(SHOP_NOTIFICATION_EMAIL='shop@example.com')
    def test_message_is_saved_and_shop_notified(self):
        response = APIClient().post('/api/content/contact/', {
            'name': 'Mia', 'email': 'mia@example.com', 'subject': 'Birthday cake', 'message': 'Can I order a cake for Saturday?',
        })
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(ContactMessage.objects.get().subject, 'Birthday cake')
        self.assertEqual(mail.outbox[0].to, ['shop@example.com'])

    def test_invalid_email_is_rejected(self):
        response = APIClient().post('/api/content/contact/', {'name': 'Mia', 'email': 'nope', 'message': 'Hi'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_honeypot_submissions_are_dropped(self):
        response = APIClient().post('/api/content/contact/', {
            'name': 'Bot', 'email': 'bot@example.com', 'message': 'Buy now', 'website': 'http://spam.example',
        })
        self.assertEqual(response.status_code, 201)
        self.assertFalse(ContactMessage.objects.exists())

    def test_rate_limited(self):
        client = APIClient()
        payload = {'name': 'Mia', 'email': 'mia@example.com', 'message': 'Hi'}
        codes = [client.post('/api/content/contact/', payload).status_code for _ in range(11)]
        self.assertEqual(codes[-1], 429)


class NewsletterTests(TestCase):
    def test_subscribe_is_idempotent_and_unsubscribe_works(self):
        client = APIClient()
        self.assertEqual(client.post('/api/content/newsletter/', {'email': 'Mia@Example.com'}).status_code, 201)
        self.assertEqual(client.post('/api/content/newsletter/', {'email': 'mia@example.com'}).status_code, 201)
        subscriber = NewsletterSubscriber.objects.get()
        self.assertEqual(subscriber.email, 'mia@example.com')

        response = client.post('/api/content/newsletter/unsubscribe/', {'token': str(subscriber.token)})
        self.assertEqual(response.status_code, 200)
        subscriber.refresh_from_db()
        self.assertFalse(subscriber.is_active)

        # Subscribing again reactivates the address.
        client.post('/api/content/newsletter/', {'email': 'mia@example.com'})
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)

    def test_unknown_unsubscribe_token(self):
        response = APIClient().post('/api/content/newsletter/unsubscribe/', {'token': '00000000-0000-0000-0000-000000000000'})
        self.assertEqual(response.status_code, 404)


class BlogTests(TestCase):
    def setUp(self):
        now = timezone.now()
        Post.objects.create(title='Our sourdough starter', body='Ten years old.\n\nFed daily.', published_at=now - timedelta(days=1))
        Post.objects.create(title='Christmas Stollen', body='Coming soon', published_at=now + timedelta(days=30))
        Post.objects.create(title='Draft post', body='Not ready')

    def test_only_published_posts_are_listed(self):
        titles = [p['title'] for p in APIClient().get('/api/content/posts/').json()]
        self.assertEqual(titles, ['Our sourdough starter'])

    def test_detail_by_slug_and_drafts_are_hidden(self):
        response = APIClient().get('/api/content/posts/our-sourdough-starter/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Fed daily.', response.json()['body'])
        self.assertEqual(APIClient().get('/api/content/posts/draft-post/').status_code, 404)

    def test_slugs_are_unique(self):
        second = Post.objects.create(title='Our sourdough starter', body='Again')
        self.assertEqual(second.slug, 'our-sourdough-starter-2')


class LanguageTests(TestCase):
    """The API answers in the language the shop asks for."""

    def test_messages_follow_accept_language(self):
        client = APIClient()
        german = client.post('/api/content/newsletter/', {'email': 'de@example.com'}, HTTP_ACCEPT_LANGUAGE='de')
        self.assertEqual(german.json()['message'], 'Danke, du bist angemeldet!')
        english = client.post('/api/content/newsletter/', {'email': 'en@example.com'}, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(english.json()['message'], "You're subscribed. Thanks!")

    def test_built_in_validation_messages_are_translated(self):
        response = APIClient().post('/api/content/newsletter/', {}, HTTP_ACCEPT_LANGUAGE='de')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Dieses Feld ist erforderlich.', response.json()['email'])
