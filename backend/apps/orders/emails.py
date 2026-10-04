"""Order emails: confirmation and cancellation for the customer (in the
language they shopped in) and a new-order alert for the bakery.

Sending never breaks an order: failures are logged. Without an SMTP server
(settings.EMAIL_HOST) emails are printed to the console.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _, override

from apps.shop import config as shop_config

logger = logging.getLogger(__name__)


def _context(order, **extra):
    items = list(order.order_items.select_related('product'))
    for item in items:
        name_en = getattr(item.product, 'name_en', '')
        item.display_name = name_en if order.language != 'de' and name_en else item.product.name
    requested = timezone.localtime(order.requested_time) if order.requested_time else None
    shop = shop_config.get()
    return {
        'order': order,
        'items': items,
        'requested': requested,
        'is_delivery': order.fulfillment_method == order.FulfillmentChoices.DELIVERY,
        'payment': getattr(order, 'order_payment', None),
        'shop_name': shop.name,
        'shop_address': shop_config.address_line(shop),
        'order_url': f"{settings.FRONTEND_URL.rstrip('/')}/orders/{order.pk}",
        'customer_name': order.customer.user.first_name if order.customer.user else '',
        **extra,
    }


def _send(subject, template, context, to, language):
    if not to:
        return
    with override(language):
        text = render_to_string(f'orders/email/{template}.txt', context)
        html = render_to_string(f'orders/email/{template}.html', context)
    message = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, to)
    message.attach_alternative(html, 'text/html')
    try:
        message.send()
    except Exception:
        logger.exception('Could not send "%s" email for order %s', template, context['order'].order_number)


def order_placed(order):
    """Confirmation to the customer and an alert for the bakery."""
    context = _context(order)
    with override(order.language):
        subject = _('Your order %(number)s at %(shop)s') % {'number': order.order_number, 'shop': context['shop_name']}
    _send(subject, 'order_placed', context, [order.customer.user.email], order.language)

    notify = shop_config.get().notification_email
    if notify:
        # The bakery reads German.
        with override('de'):
            subject = _('New order %(number)s') % {'number': order.order_number}
        _send(subject, 'shop_new_order', {**context, 'order_url': _admin_url(order)},
              [notify], 'de')


def order_canceled(order, reason=''):
    context = _context(order, reason=reason)
    with override(order.language):
        subject = _('Your order %(number)s was canceled') % {'number': order.order_number}
    _send(subject, 'order_canceled', context, [order.customer.user.email], order.language)


def _admin_url(order):
    return f"{settings.FRONTEND_URL.rstrip('/')}/admin/orders"
