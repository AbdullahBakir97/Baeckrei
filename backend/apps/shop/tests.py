from datetime import date, datetime, timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.orders import slots
from apps.orders.models import Order

from . import config
from .models import ClosingDay, ShopSettings

HOURS = 'mon-sun 08:00-12:00'


def berlin(*args):
    return timezone.make_aware(datetime(*args), timezone.get_current_timezone())


@override_settings(SHOP_OPENING_HOURS=HOURS, SHOP_DELIVERY_FEE=Decimal('3.50'), DELIVERY_FEE=Decimal('3.50'),
                   SHOP_PICKUP_LEAD_MINUTES=60, SHOP_SLOT_MINUTES=60, SHOP_NAME='Backlover')
class ConfigTests(TestCase):
    def test_server_settings_apply_until_saved(self):
        shop = config.get()
        self.assertEqual(shop.name, 'Backlover')
        self.assertEqual(shop.delivery_fee, Decimal('3.50'))
        self.assertEqual(len(shop.opening_hours[0]), 1)

    def test_saved_values_win(self):
        ShopSettings.objects.create(name='Bäckerei Sonne', delivery_fee=Decimal('2.00'),
                                    opening_hours={'0': [['06:00', '10:00'], ['15:00', '18:00']]})
        shop = config.get()
        self.assertEqual(shop.name, 'Bäckerei Sonne')
        self.assertEqual(shop.delivery_fee, Decimal('2.00'))
        self.assertEqual(len(shop.opening_hours[0]), 2)
        self.assertEqual(shop.opening_hours.get(1, []), [])  # Tuesday not listed: closed

    def test_closing_days_have_no_slots(self):
        monday = berlin(2026, 10, 5, 6, 0)
        ClosingDay.objects.create(start=date(2026, 10, 5), label='Betriebsferien')
        starts = [s['start'] for s in slots.available_slots(Order.FulfillmentChoices.PICKUP, now=monday, days=2)]
        self.assertTrue(starts)
        self.assertTrue(all(s.date() == date(2026, 10, 6) for s in starts))

    def test_opening_status_on_a_closing_day(self):
        ClosingDay.objects.create(start=timezone.localdate(), end=timezone.localdate() + timedelta(days=1), label='Urlaub')
        status = slots.opening_status(now=timezone.now().replace(hour=9))
        self.assertFalse(status['open_now'])
        self.assertEqual(status['closed_today'], 'Urlaub')
        self.assertEqual(status['closures'][0]['label'], 'Urlaub')

    def test_switching_delivery_off(self):
        ShopSettings.objects.create(delivery_enabled=False)
        self.assertEqual(slots.available_slots(Order.FulfillmentChoices.DELIVERY), [])
        self.assertTrue(slots.method_enabled(Order.FulfillmentChoices.PICKUP))

    def test_public_info(self):
        ShopSettings.objects.create(phone='030 123', postal_code='10117', announcement='Heute Brezeltag', announcement_active=True)
        data = APIClient().get('/api/shop/info/').json()
        self.assertEqual(data['phone'], '030 123')
        self.assertEqual(data['postal_code'], '10117')
        self.assertEqual(data['announcement'], 'Heute Brezeltag')
        self.assertIn('days', data['hours'])
        self.assertNotIn('notification_email', data)

    def test_inactive_announcement_is_hidden(self):
        ShopSettings.objects.create(announcement='Old news', announcement_active=False)
        self.assertEqual(APIClient().get('/api/shop/info/').json()['announcement'], '')
