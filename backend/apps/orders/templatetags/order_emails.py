"""Formatting for order emails in the active language (de or en)."""
from decimal import Decimal

from django import template
from django.utils import formats
from django.utils.translation import get_language

register = template.Library()


@register.filter
def euro(value):
    amount = Decimal(value or 0).quantize(Decimal('0.01'))
    if (get_language() or 'de').startswith('de'):
        return f"{formats.number_format(amount, 2, use_l10n=True)} €"
    return f"€{amount:,.2f}"


@register.filter
def when(value):
    if not value:
        return ''
    if (get_language() or 'de').startswith('de'):
        return formats.date_format(value, 'l, j. F, H:i') + ' Uhr'
    return formats.date_format(value, 'l j F, H:i')


@register.filter
def percent(rate):
    return f"{Decimal(rate) * 100:.0f} %" if (get_language() or 'de').startswith('de') else f"{Decimal(rate) * 100:.0f}%"
