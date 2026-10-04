"""Pickup and delivery times offered at checkout.

Slots come from the shop's opening hours, set in the admin or, until then,
in settings.SHOP_OPENING_HOURS, e.g.

    mon-fri 07:00-18:00; sat 08:00-14:00

Days that are not listed are closed. A day may have several ranges
("mon 07:00-12:00 14:00-18:00"). Each slot is SHOP_SLOT_MINUTES long and
starts at least the lead time from now, so the bakery has time to pack (or
bake) the order. With SHOP_SLOT_CAPACITY set, a full slot is shown as taken.
Closing days (holidays) have no slots. All values come from apps.shop.config.
"""
import re
from datetime import datetime, time, timedelta

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count
from django.utils import timezone

DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
_RANGE = re.compile(r'^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$')


def _day_numbers(spec):
    if '-' in spec:
        first, last = spec.split('-', 1)
        start, end = DAYS.index(first), DAYS.index(last)
        return list(range(start, end + 1)) if start <= end else list(range(start, 7)) + list(range(0, end + 1))
    return [DAYS.index(spec)]


def parse_opening_hours(text):
    """'mon-fri 07:00-18:00; sat 08:00-14:00' -> {weekday: [(open, close), ...]}."""
    hours = {}
    for part in filter(None, (p.strip().lower() for p in (text or '').split(';'))):
        day_spec, *ranges = part.split()
        try:
            days = _day_numbers(day_spec)
        except ValueError:
            raise ImproperlyConfigured(f'SHOP_OPENING_HOURS: unknown day "{day_spec}"')
        if ranges == ['closed']:
            for day in days:
                hours[day] = []
            continue
        for value in ranges:
            match = _RANGE.match(value)
            if not match:
                raise ImproperlyConfigured(f'SHOP_OPENING_HOURS: "{value}" is not a time range like 07:00-18:00')
            h1, m1, h2, m2 = map(int, match.groups())
            opens, closes = time(h1, m1), time(h2, m2)
            if closes <= opens:
                raise ImproperlyConfigured(f'SHOP_OPENING_HOURS: "{value}" closes before it opens')
            for day in days:
                hours.setdefault(day, []).append((opens, closes))
    return hours


def _config():
    from apps.shop import config
    return config.get()


def opening_hours():
    return _config().opening_hours


def lead_minutes(method, config=None):
    from .models import Order
    config = config or _config()
    if method == Order.FulfillmentChoices.DELIVERY:
        return config.delivery_lead_minutes
    return config.pickup_lead_minutes


def method_enabled(method, config=None):
    from .models import Order
    config = config or _config()
    if method == Order.FulfillmentChoices.DELIVERY:
        return config.delivery_enabled
    return config.pickup_enabled


def closed_on(day, config):
    """The closing day entry covering `day`, if any."""
    return next((closure for closure in config.closures if closure.covers(day)), None)


def _slot_starts(method, now, days, config):
    step = timedelta(minutes=config.slot_minutes)
    earliest = now + timedelta(minutes=lead_minutes(method, config))
    tz = timezone.get_current_timezone()
    today = timezone.localtime(now, tz).date()
    for offset in range(days):
        day = today + timedelta(days=offset)
        if closed_on(day, config):
            continue
        for opens, closes in config.opening_hours.get(day.weekday(), []):
            start = timezone.make_aware(datetime.combine(day, opens), tz)
            end = timezone.make_aware(datetime.combine(day, closes), tz)
            while start + step <= end:
                if start >= earliest:
                    yield start
                start += step


def available_slots(method, now=None, days=None, config=None):
    """Upcoming slots as [{'start': datetime, 'available': bool}], soonest first."""
    from .models import Order
    config = config or _config()
    if not method_enabled(method, config):
        return []
    now = now or timezone.now()
    starts = list(_slot_starts(method, now, days or config.slot_days, config))
    taken = set()
    capacity = config.slot_capacity
    if capacity and starts:
        booked = (
            Order.objects.filter(requested_time__in=starts)
            .exclude(status=Order.StatusChoices.CANCELED)
            .values('requested_time').annotate(count=Count('id'))
        )
        taken = {row['requested_time'] for row in booked if row['count'] >= capacity}
    return [{'start': start, 'available': start not in taken} for start in starts]


def is_bookable(method, requested_time, now=None):
    return any(
        slot['available'] and slot['start'] == requested_time
        for slot in available_slots(method, now=now)
    )


def opening_status(now=None, days=7, config=None):
    """Today's hours and whether the shop is open, for screens and the footer.

    Returns {'days': [{'weekday': 0-6, 'ranges': [['07:00', '18:00'], ...]}],
    'open_now': bool, 'closes_at': 'HH:MM' | None, 'next_open': ISO datetime | None,
    'closed_today': label | None, 'closures': [upcoming closing days]}.
    """
    config = config or _config()
    tz = timezone.get_current_timezone()
    now = timezone.localtime(now or timezone.now(), tz)
    hours = config.opening_hours
    today_closure = closed_on(now.date(), config)
    status = {
        'time_zone': str(tz),
        'days': [
            {'weekday': day, 'ranges': [[o.strftime('%H:%M'), c.strftime('%H:%M')] for o, c in hours.get(day, [])]}
            for day in range(7)
        ],
        'open_now': False,
        'closes_at': None,
        'next_open': None,
        'closed_today': (today_closure.label or True) if today_closure else None,
        'closures': [
            {'start': c.start.isoformat(), 'end': c.last_day.isoformat(), 'label': c.label, 'label_en': c.label_en}
            for c in config.closures
        ],
    }
    if not today_closure:
        for opens, closes in hours.get(now.weekday(), []):
            if opens <= now.time() < closes:
                status['open_now'] = True
                status['closes_at'] = closes.strftime('%H:%M')
                return status
    for offset in range(days + 31):
        day = now.date() + timedelta(days=offset)
        if closed_on(day, config):
            continue
        for opens, _closes in sorted(hours.get(day.weekday(), [])):
            start = timezone.make_aware(datetime.combine(day, opens), tz)
            if start > now:
                status['next_open'] = start.isoformat()
                return status
    return status
