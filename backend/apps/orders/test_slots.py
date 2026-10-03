from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings

from apps.orders.slots import available_slots, is_bookable, parse_opening_hours

BERLIN = ZoneInfo('Europe/Berlin')
HOURS = 'mon-fri 07:00-09:00; sat 08:00-09:00'


def berlin(*args):
    return datetime(*args, tzinfo=BERLIN)


class OpeningHoursTests(SimpleTestCase):
    def test_parses_day_ranges_split_hours_and_closed_days(self):
        hours = parse_opening_hours('mon-wed 07:00-12:00 14:00-18:00; sat 08:00-13:00; sun closed')
        self.assertEqual(hours[0], [(time(7), time(12)), (time(14), time(18))])
        self.assertEqual(hours[2], hours[0])
        self.assertNotIn(3, hours)  # Thursday not listed: closed
        self.assertEqual(hours[5], [(time(8), time(13))])
        self.assertEqual(hours[6], [])

    def test_day_range_can_wrap_over_the_weekend(self):
        self.assertEqual(sorted(parse_opening_hours('sat-mon 08:00-10:00')), [0, 5, 6])

    def test_rejects_nonsense(self):
        for text in ('funday 08:00-10:00', 'mon 8-10', 'mon 10:00-08:00'):
            with self.assertRaises(ImproperlyConfigured, msg=text):
                parse_opening_hours(text)


@override_settings(SHOP_OPENING_HOURS=HOURS, SHOP_SLOT_MINUTES=30, SHOP_SLOT_DAYS=7,
                   SHOP_PICKUP_LEAD_MINUTES=60, SHOP_DELIVERY_LEAD_MINUTES=120, SHOP_SLOT_CAPACITY=0,
                   TIME_ZONE='Europe/Berlin')
class SlotTests(TestCase):
    # Wednesday 1 October 2026, 06:10 in Berlin.
    now = berlin(2026, 10, 1, 6, 10)

    def starts(self, method='pickup'):
        return [slot['start'] for slot in available_slots(method, now=self.now)]

    def test_slots_follow_opening_hours_and_lead_time(self):
        starts = self.starts()
        # Opens 07:00, but pickup needs an hour: first slot 07:30; the last
        # one starts half an hour before closing.
        self.assertEqual(starts[:3], [berlin(2026, 10, 1, 7, 30), berlin(2026, 10, 1, 8, 0), berlin(2026, 10, 1, 8, 30)])
        self.assertEqual(starts[3], berlin(2026, 10, 2, 7, 0))
        # Saturday has two slots, Sunday none.
        self.assertIn(berlin(2026, 10, 3, 8, 30), starts)
        self.assertFalse([s for s in starts if s.date() == datetime(2026, 10, 4).date()])

    def test_delivery_needs_more_lead_time(self):
        self.assertEqual(self.starts('delivery')[0], berlin(2026, 10, 1, 8, 30))

    def test_is_bookable_only_for_real_slots(self):
        self.assertTrue(is_bookable('pickup', berlin(2026, 10, 1, 8, 0), now=self.now))
        self.assertFalse(is_bookable('pickup', berlin(2026, 10, 1, 7, 0), now=self.now))  # too soon
        self.assertFalse(is_bookable('pickup', berlin(2026, 10, 1, 8, 15), now=self.now))  # off the grid
        self.assertFalse(is_bookable('pickup', berlin(2026, 10, 4, 8, 0), now=self.now))  # closed

    @override_settings(SHOP_SLOT_CAPACITY=1)
    def test_full_slots_are_shown_as_taken(self):
        from apps.orders.tests import make_order
        from django.contrib.auth import get_user_model
        from apps.core.testing import make_test_password

        user = get_user_model().objects.create_user(email='slot@example.com', password=make_test_password())
        order = make_order(user)
        order.requested_time = berlin(2026, 10, 1, 8, 0)
        order.save()
        slots = {slot['start']: slot['available'] for slot in available_slots('pickup', now=self.now)}
        self.assertFalse(slots[berlin(2026, 10, 1, 8, 0)])
        self.assertTrue(slots[berlin(2026, 10, 1, 8, 30)])
        self.assertFalse(is_bookable('pickup', berlin(2026, 10, 1, 8, 0), now=self.now))

        # A canceled order frees its slot again.
        order.status = order.StatusChoices.CANCELED
        order.save()
        self.assertTrue(is_bookable('pickup', berlin(2026, 10, 1, 8, 0), now=self.now))


@override_settings(SHOP_OPENING_HOURS=HOURS, TIME_ZONE='Europe/Berlin')
class OpeningStatusTests(TestCase):
    def test_open_now_with_closing_time(self):
        from apps.orders.slots import opening_status
        status = opening_status(now=berlin(2026, 10, 1, 8, 15))
        self.assertTrue(status['open_now'])
        self.assertEqual(status['closes_at'], '09:00')
        self.assertEqual(status['days'][0]['ranges'], [['07:00', '09:00']])
        self.assertEqual(status['days'][6]['ranges'], [])

    def test_closed_shows_next_opening(self):
        from apps.orders.slots import opening_status
        status = opening_status(now=berlin(2026, 10, 3, 10, 0))  # Saturday after closing
        self.assertFalse(status['open_now'])
        self.assertEqual(status['next_open'], berlin(2026, 10, 5, 7, 0).isoformat())  # Monday

    def test_public_endpoint(self):
        response = self.client.get('/api/orders/opening-hours/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['days']), 7)
