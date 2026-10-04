from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.content.models import ContactMessage, NewsletterCampaign, NewsletterSubscriber, Post
from apps.menuboard.models import MenuScreen, MenuSlide
from apps.products.models import AllergenInfo, Category, Ingredient, Product
from apps.shop.models import ShopSettings

User = get_user_model()


class StudioTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email='chef@example.com', password='Pass12345!')
        self.client = APIClient()
        self.client.force_authenticate(self.admin)


class AccessTests(TestCase):
    def test_only_staff(self):
        customer = User.objects.create_user(email='kunde@example.com', password='Pass12345!')
        client = APIClient()
        for url in ('/api/studio/summary/', '/api/studio/settings/', '/api/studio/messages/', '/api/studio/menu-screens/'):
            self.assertIn(client.get(url).status_code, (401, 403), url)
            client.force_authenticate(customer)
            self.assertEqual(client.get(url).status_code, 403, url)
            client.force_authenticate(None)


@override_settings(SHOP_OPENING_HOURS='mon-fri 07:00-18:00')
class SettingsTests(StudioTestCase):
    def test_shows_effective_values_and_saves(self):
        data = self.client.get('/api/studio/settings/').json()
        self.assertEqual(data['effective']['opening_hours']['0'], [['07:00', '18:00']])
        response = self.client.patch('/api/studio/settings/', {
            'opening_hours': {'0': [['08:00', '12:00'], ['06:00', '07:00']], '5': [['08:00', '13:00']]},
            'delivery_fee': '2.50', 'phone': '030 999',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        saved = ShopSettings.load()
        self.assertEqual(saved.opening_hours['0'], [['06:00', '07:00'], ['08:00', '12:00']])
        self.assertEqual(saved.opening_hours['2'], [])
        self.assertEqual(response.json()['effective']['delivery_fee'], '2.50')

    def test_rejects_bad_hours(self):
        response = self.client.patch('/api/studio/settings/', {'opening_hours': {'0': [['18:00', '07:00']]}}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_closing_days(self):
        today = timezone.localdate()
        response = self.client.post('/api/studio/closing-days/', {'start': str(today), 'end': str(today - timedelta(days=1))})
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/studio/closing-days/', {'start': str(today), 'label': 'Inventur'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.client.get('/api/studio/closing-days/?upcoming=true').json()), 1)


class PostTests(StudioTestCase):
    def test_draft_schedule_publish(self):
        response = self.client.post('/api/studio/posts/', {'title': 'Sauerteig', 'body': 'Absatz eins\n\nAbsatz zwei',
                                                           'title_en': 'Sourdough'})
        self.assertEqual(response.status_code, 201, response.content)
        post = Post.objects.get()
        self.assertEqual(post.author, self.admin)
        self.assertEqual(response.json()['state'], 'draft')
        later = (timezone.now() + timedelta(days=2)).isoformat()
        self.assertEqual(self.client.patch(f'/api/studio/posts/{post.pk}/', {'published_at': later}).json()['state'], 'scheduled')
        public = lambda: (lambda d: d['results'] if isinstance(d, dict) else d)(APIClient().get('/api/content/posts/').json())
        self.assertEqual(public(), [])
        self.client.patch(f'/api/studio/posts/{post.pk}/', {'published_at': timezone.now().isoformat()})
        self.assertEqual(public()[0]['title_en'], 'Sourdough')
        self.assertEqual(len(self.client.get('/api/studio/posts/?state=published').json()), 1)

    def test_cover_image_upload_and_removal(self):
        post = Post.objects.create(title='Brot', body='Text')
        image = SimpleUploadedFile('cover.gif', b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04'
                                   b'\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
                                   content_type='image/gif')
        response = self.client.patch(f'/api/studio/posts/{post.pk}/', {'cover_image': image}, format='multipart')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()['cover_image_url'])
        response = self.client.patch(f'/api/studio/posts/{post.pk}/', {'remove_cover_image': True}, format='json')
        self.assertIsNone(response.json()['cover_image_url'])


@override_settings(SHOP_NOTIFICATION_EMAIL='laden@example.com')
class MessageTests(StudioTestCase):
    def test_reply_is_emailed_and_filed(self):
        message = ContactMessage.objects.create(name='Mia', email='mia@example.com', subject='Torte', message='Geht Samstag?')
        self.assertEqual(self.client.get('/api/studio/summary/').json()['unread_messages'], 1)
        response = self.client.post(f'/api/studio/messages/{message.pk}/reply/', {'reply': 'Ja, gerne!\n\nBis Samstag.'})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(mail.outbox[0].to, ['mia@example.com'])
        self.assertEqual(mail.outbox[0].subject, 'Re: Torte')
        self.assertEqual(mail.outbox[0].reply_to, ['laden@example.com'])
        self.assertIn('Geht Samstag?', mail.outbox[0].body)
        message.refresh_from_db()
        self.assertTrue(message.handled)
        self.assertEqual(message.replied_by, self.admin)
        self.assertEqual(len(self.client.get('/api/studio/messages/?state=open').json()), 0)


class NewsletterTests(StudioTestCase):
    def setUp(self):
        super().setUp()
        self.mia = NewsletterSubscriber.objects.create(email='mia@example.com')
        self.tom = NewsletterSubscriber.objects.create(email='tom@example.com')
        NewsletterSubscriber.objects.create(email='gone@example.com', unsubscribed_at=timezone.now())

    def test_export_and_unsubscribe(self):
        csv = self.client.get('/api/studio/subscribers/export/').content.decode()
        self.assertIn('mia@example.com', csv)
        self.assertNotIn('gone@example.com', csv)
        self.client.post(f'/api/studio/subscribers/{self.tom.pk}/unsubscribe/')
        self.assertEqual(len(self.client.get('/api/studio/subscribers/?state=active').json()), 1)

    def test_send_to_active_subscribers_once(self):
        campaign = NewsletterCampaign.objects.create(subject='Herbstgebäck', body='Neu: Kürbisbrot.')
        self.assertEqual(self.client.post(f'/api/studio/campaigns/{campaign.pk}/test/').json()['sent_to'], 'chef@example.com')
        mail.outbox.clear()
        response = self.client.post(f'/api/studio/campaigns/{campaign.pk}/send/')
        self.assertEqual(response.json()['recipient_count'], 2)
        self.assertEqual(sorted(m.to[0] for m in mail.outbox), ['mia@example.com', 'tom@example.com'])
        mia_mail = next(m for m in mail.outbox if m.to == ['mia@example.com'])
        self.assertIn(str(self.mia.token), mia_mail.body)
        self.assertIn('List-Unsubscribe', mia_mail.extra_headers)
        self.assertEqual(self.client.post(f'/api/studio/campaigns/{campaign.pk}/send/').status_code, 400)
        self.assertEqual(self.client.patch(f'/api/studio/campaigns/{campaign.pk}/', {'subject': 'X'}).status_code, 400)
        self.assertEqual(self.client.delete(f'/api/studio/campaigns/{campaign.pk}/').status_code, 400)


class RecipeTests(StudioTestCase):
    def setUp(self):
        super().setUp()
        category = Category.objects.create(name='Brot')
        self.product = Product.objects.create(
            name='Roggenbrot', description='Rye', category=category, price=Decimal('3.50'), stock=5,
            image=SimpleUploadedFile('rye.png', b'\x89PNG', content_type='image/png'))

    def test_allergens_ingredients_and_nutrition(self):
        gluten = self.client.post('/api/studio/allergens/', {'name': 'Gluten'}).json()
        self.assertEqual(self.client.post('/api/studio/allergens/', {'name': 'gluten'}).status_code, 400)
        flour = self.client.post('/api/studio/ingredients/', {'name': 'Roggenmehl', 'allergens': [gluten['id']]},
                                 format='json').json()
        response = self.client.put(f'/api/studio/products/{self.product.pk}/recipe/', {
            'ingredients': [flour['id']],
            'nutrition': {'calories': '210', 'proteins': '6', 'carbohydrates': '40', 'fats': '1.2', 'fiber': '8'},
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['allergens'], ['Gluten'])
        self.assertEqual(response.json()['nutrition']['calories'], '210.00')
        # In use: cannot be deleted
        self.assertEqual(self.client.delete(f"/api/studio/ingredients/{flour['id']}/").status_code, 400)
        self.assertEqual(self.client.delete(f"/api/studio/allergens/{gluten['id']}/").status_code, 400)
        response = self.client.put(f'/api/studio/products/{self.product.pk}/recipe/', {'ingredients': [], 'nutrition': None},
                                   format='json')
        self.assertIsNone(response.json()['nutrition'])
        self.assertEqual(self.client.delete(f"/api/studio/ingredients/{flour['id']}/").status_code, 204)
        self.assertFalse(Ingredient.objects.exists())
        self.assertTrue(AllergenInfo.objects.exists())


class ScreenTests(StudioTestCase):
    def test_design_reload_and_duplicate(self):
        response = self.client.post('/api/studio/menu-screens/', {
            'name': 'Schaufenster', 'layout': 'grid', 'theme': 'custom', 'accent_color': '#ff8800',
            'categories': [], 'ticker': 'Heute: Brezeltag',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        screen = response.json()
        self.assertEqual(len(screen['code']), 4)
        bad = self.client.patch(f"/api/studio/menu-screens/{screen['id']}/", {'accent_color': 'orange'}, format='json')
        self.assertEqual(bad.status_code, 400)
        slide = self.client.post('/api/studio/menu-slides/', {'screen': screen['id'], 'title': 'Frühstück',
                                                             'price': '3.90', 'weekdays': [0, 1, 2, 3, 4]}, format='json')
        self.assertEqual(slide.status_code, 201, slide.content)
        self.assertEqual(self.client.post(f"/api/studio/menu-screens/{screen['id']}/reload/").json()['reload_token'], 1)
        copy = self.client.post(f"/api/studio/menu-screens/{screen['id']}/duplicate/").json()
        self.assertNotEqual(copy['code'], screen['code'])
        self.assertEqual(MenuSlide.objects.filter(screen_id=copy['id']).count(), 1)
        self.assertEqual(MenuScreen.objects.count(), 2)
        board = APIClient().get(f"/api/menu-screens/{screen['slug']}/board/").json()
        self.assertEqual(board['screen']['ticker'], 'Heute: Brezeltag')
