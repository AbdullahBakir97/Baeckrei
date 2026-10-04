"""The shop's settings as the rest of the code uses them: values saved in
the admin (ShopSettings, ClosingDay), else the SHOP_* server settings."""
import re
from datetime import time
from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings
from django.utils import timezone

_TIME = re.compile(r'^(\d{1,2}):(\d{2})$')


def _parse_time(value):
    match = _TIME.match(str(value).strip())
    if not match:
        raise ValueError(f'"{value}" is not a time like 07:00')
    hour, minute = map(int, match.groups())
    if hour > 23 or minute > 59:
        raise ValueError(f'"{value}" is not a valid time')
    return time(hour, minute)


def parse_weekly_hours(data):
    """{"0": [["07:00", "18:00"]]} -> {0: [(time(7), time(18))]}; validates."""
    hours = {}
    for day, ranges in (data or {}).items():
        weekday = int(day)
        if not 0 <= weekday <= 6:
            raise ValueError(f'Unknown weekday {day}')
        parsed = []
        for opens, closes in ranges or []:
            start, end = _parse_time(opens), _parse_time(closes)
            if end <= start:
                raise ValueError(f'{opens}–{closes} closes before it opens')
            parsed.append((start, end))
        hours[weekday] = sorted(parsed)
    return hours


def _pick(saved, fallback):
    return fallback if saved in (None, '') else saved


def get():
    """Everything in one object; read it once per request."""
    from .models import ClosingDay, ShopSettings
    from apps.orders.slots import parse_opening_hours

    row = ShopSettings.load()
    hours = parse_weekly_hours(row.opening_hours) if row.opening_hours else parse_opening_hours(settings.SHOP_OPENING_HOURS)
    today = timezone.localdate()
    return SimpleNamespace(
        name=_pick(row.name, settings.SHOP_NAME),
        legal_name=row.legal_name,
        owner=row.owner,
        street=_pick(row.street, settings.SHOP_STREET),
        house_number=row.house_number,
        postal_code=row.postal_code,
        city=_pick(row.city, settings.SHOP_CITY),
        country=row.country,
        transit=row.transit,
        phone=row.phone,
        email=row.email,
        vat_id=row.vat_id,
        register=row.register,
        instagram=row.instagram,
        facebook=row.facebook,
        twitter=row.twitter,
        notification_email=_pick(row.notification_email, settings.SHOP_NOTIFICATION_EMAIL),
        opening_hours=hours,
        pickup_enabled=row.pickup_enabled,
        delivery_enabled=row.delivery_enabled,
        delivery_fee=Decimal(_pick(row.delivery_fee, settings.DELIVERY_FEE)),
        pickup_lead_minutes=_pick(row.pickup_lead_minutes, settings.SHOP_PICKUP_LEAD_MINUTES),
        delivery_lead_minutes=_pick(row.delivery_lead_minutes, settings.SHOP_DELIVERY_LEAD_MINUTES),
        slot_minutes=_pick(row.slot_minutes, settings.SHOP_SLOT_MINUTES) or 30,
        slot_days=_pick(row.slot_days, settings.SHOP_SLOT_DAYS) or 7,
        slot_capacity=_pick(row.slot_capacity, settings.SHOP_SLOT_CAPACITY),
        announcement=row.announcement if row.announcement_active else '',
        announcement_en=row.announcement_en if row.announcement_active else '',
        closures=list(ClosingDay.objects.filter(end__gte=today) | ClosingDay.objects.filter(end__isnull=True, start__gte=today)),
    )


def address_line(config):
    street = ' '.join(filter(None, [config.street, config.house_number]))
    city = ' '.join(filter(None, [config.postal_code, config.city]))
    return ', '.join(filter(None, [street, city]))
