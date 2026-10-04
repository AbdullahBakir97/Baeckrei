from datetime import time, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.products.models import Category, Product

from .models import MenuScreen, MenuSlide


def product(name, category, **extra):
    return Product.objects.create(
        name=name, description=name, category=category, price=Decimal('2.00'), stock=extra.pop('stock', 10),
        status='active', available=True, image=SimpleUploadedFile(f'{name}.png', b'\x89PNG', content_type='image/png'),
        **extra,
    )


class BoardTests(TestCase):
    def setUp(self):
        self.bread = Category.objects.create(name='Brot', order=2)
        self.cakes = Category.objects.create(name='Kuchen', order=1)
        self.rye = product('Roggenbrot', self.bread)
        self.cake = product('Käsekuchen', self.cakes)
        self.empty = product('Brezel', self.bread, stock=0)
        self.client = APIClient()

    def test_default_board_without_screens(self):
        data = self.client.get('/api/menu-screens/default/board/').json()
        self.assertEqual(data['screen']['layout'], 'columns')
        names = [c['name'] for c in data['categories']]
        self.assertLess(names.index('Kuchen'), names.index('Brot'))  # by position
        self.assertEqual(len(data['products']), 3)
        self.assertIn('open_now', data['status'])

    def test_screen_categories_hidden_and_sold_out(self):
        screen = MenuScreen.objects.create(name='Theke', categories=[self.bread.pk], hidden_products=[str(self.rye.pk)],
                                           sold_out='hide')
        data = self.client.get(f'/api/menu-screens/{screen.slug}/board/').json()
        self.assertEqual([c['name'] for c in data['categories']], ['Brot'])
        self.assertEqual(data['products'], [])

    def test_slides_follow_their_schedule(self):
        screen = MenuScreen.objects.create(name='Fenster')
        MenuSlide.objects.create(screen=screen, title='Immer')
        MenuSlide.objects.create(screen=screen, title='Vorbei', end_date=timezone.localdate() - timedelta(days=1))
        MenuSlide.objects.create(screen=screen, title='Aus', active=False)
        slide = MenuSlide(screen=screen, title='Frühstück', start_time=time(7), end_time=time(11))
        self.assertTrue(slide.runs_at(timezone.now().replace(hour=8)))
        self.assertFalse(slide.runs_at(timezone.now().replace(hour=12)))
        titles = [s['title'] for s in self.client.get(f'/api/menu-screens/{screen.slug}/board/').json()['slides']]
        self.assertEqual(titles, ['Immer'])

    def test_arabic_texts(self):
        screen = MenuScreen.objects.create(name='Fenster', language='de_ar', headline_ar='مخبزنا', ticker_ar='بريتسل طازج')
        MenuSlide.objects.create(screen=screen, style='text', title='Frühstück', title_ar='الفطور', text_ar='قهوة وكرواسون')
        data = self.client.get(f'/api/menu-screens/{screen.slug}/board/').json()
        self.assertEqual(data['screen']['language'], 'de_ar')
        self.assertEqual(data['screen']['headline_ar'], 'مخبزنا')
        self.assertEqual(data['screen']['ticker_ar'], 'بريتسل طازج')
        self.assertEqual(data['slides'][0]['title_ar'], 'الفطور')
        self.assertEqual(data['slides'][0]['text_ar'], 'قهوة وكرواسون')

    def test_codes_slugs_and_one_default(self):
        first = MenuScreen.objects.create(name='Theke', is_default=True)
        second = MenuScreen.objects.create(name='Theke', is_default=True)
        self.assertEqual(len(first.code), 4)
        self.assertNotEqual(first.slug, second.slug)
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertEqual(self.client.get('/api/menu-screens/default/board/').json()['screen']['slug'], second.slug)

    def test_pairing_with_the_code(self):
        screen = MenuScreen.objects.create(name='Fenster')
        self.assertEqual(self.client.get(f'/api/menu-screens/pair/{screen.code}/').json()['slug'], screen.slug)
        wrong = '0000' if screen.code != '0000' else '0001'
        self.assertEqual(self.client.get(f'/api/menu-screens/pair/{wrong}/').status_code, 404)

    def test_heartbeat_marks_the_screen_online(self):
        screen = MenuScreen.objects.create(name='Fenster', reload_token=3)
        self.assertFalse(screen.online)
        response = self.client.post(f'/api/menu-screens/{screen.slug}/heartbeat/', {'width': 1920, 'height': 1080}, format='json')
        self.assertEqual(response.json()['reload_token'], 3)
        screen.refresh_from_db()
        self.assertTrue(screen.online)
        self.assertEqual(screen.last_seen_info['width'], '1920')
