"""Online payment with Stripe Checkout.

The customer places the order as usual (stock is reserved), then pays on
Stripe's hosted page, which offers cards, Apple Pay, Google Pay and whatever
else is switched on in the Stripe dashboard. Stripe reports the result to
the webhook; only then is the payment marked as paid and the confirmation
email sent. An unpaid order gives its stock back when the payment page
expires (settings.STRIPE_CHECKOUT_MINUTES).
"""
import logging
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _, override

from .models import Order, Payment


def shop_name():
    from apps.shop import config
    return config.get().name

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Online payment could not be started; the message is shown to the customer."""


def _cents(amount):
    return int((Decimal(amount) * 100).quantize(Decimal('1')))


def _product_name(product, language):
    if language == 'en' and getattr(product, 'name_en', ''):
        return product.name_en
    return product.name


def _session_info(payment):
    return payment.payment_gateway_response or {}


def start_checkout(order):
    """Return the URL of a Stripe payment page for the order."""
    if not settings.STRIPE_ENABLED:
        raise PaymentError(_('Online payment is not available.'))
    payment = getattr(order, 'order_payment', None)
    if payment is None or not payment.is_online or payment.status != Payment.PaymentStatus.PENDING:
        raise PaymentError(_('This order does not need to be paid online.'))
    if order.status != Order.StatusChoices.PENDING:
        raise PaymentError(_('This order can no longer be paid.'))

    # Reuse the payment page while it is still open (e.g. after a reload).
    session_id = _session_info(payment).get('checkout_session')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id, api_key=settings.STRIPE_SECRET_KEY)
            if session.status == 'open':
                return session.url
        except stripe.StripeError:
            logger.warning('Could not reuse Stripe session %s', session_id, exc_info=True)

    base = settings.FRONTEND_URL.rstrip('/')
    items = list(order.order_items.select_related('product'))
    with override(order.language):
        line_items = [{
            'price_data': {
                'currency': 'eur',
                'unit_amount': _cents(item.price_per_item),
                'product_data': {'name': _product_name(item.product, order.language)},
            },
            'quantity': item.quantity,
        } for item in items]
        if order.delivery_fee:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': _cents(order.delivery_fee),
                    'product_data': {'name': _('Delivery')},
                },
                'quantity': 1,
            })
    metadata = {'order_id': str(order.pk), 'order_number': order.order_number}
    try:
        session = stripe.checkout.Session.create(
            api_key=settings.STRIPE_SECRET_KEY,
            mode='payment',
            line_items=line_items,
            client_reference_id=str(order.pk),
            customer_email=order.customer.user.email or None,
            locale=order.language,
            metadata=metadata,
            payment_intent_data={
                'metadata': metadata,
                'description': f'{shop_name()} {order.order_number}',
            },
            success_url=f'{base}/orders/{order.pk}?placed=1&paid=1',
            cancel_url=f'{base}/orders/{order.pk}?payment=canceled',
            expires_at=int((timezone.now() + timedelta(minutes=settings.STRIPE_CHECKOUT_MINUTES)).timestamp()),
        )
    except stripe.StripeError:
        logger.exception('Stripe Checkout session for order %s failed', order.order_number)
        raise PaymentError(_('Online payment is unavailable right now. Please try again in a moment.'))

    payment.transaction_id = session.id
    payment.payment_gateway_response = {'checkout_session': session.id}
    payment.save(update_fields=['transaction_id', 'payment_gateway_response', 'updated_at'])
    return session.url


def expire_checkout(payment):
    """Close an unpaid payment page so it cannot be paid any more (best effort)."""
    session_id = _session_info(payment).get('checkout_session')
    if not session_id or not settings.STRIPE_SECRET_KEY:
        return
    try:
        stripe.checkout.Session.expire(session_id, api_key=settings.STRIPE_SECRET_KEY)
    except stripe.StripeError:
        # Already expired or completed; the webhook sorts out the latter.
        logger.info('Stripe session %s could not be expired', session_id, exc_info=True)


def refund(payment):
    """Give an online payment back in full. Raises PaymentError if Stripe refuses."""
    payment_intent = _session_info(payment).get('payment_intent')
    if not payment_intent:
        raise PaymentError(_('This payment cannot be refunded automatically.'))
    try:
        stripe.Refund.create(
            api_key=settings.STRIPE_SECRET_KEY,
            payment_intent=payment_intent,
            idempotency_key=f'refund-payment-{payment.pk}',
        )
    except stripe.StripeError:
        logger.exception('Refund for payment %s failed', payment.pk)
        raise PaymentError(_('The refund failed. Please try again or refund it in the Stripe dashboard.'))
    payment.refund_payment()


# --------------------------------------------------------------------------
# Webhook
# --------------------------------------------------------------------------

def handle_webhook(payload, signature):
    """Verify and apply a Stripe event. Raises ValueError for a bad request."""
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise ValueError(str(exc))

    session = event['data']['object'].to_dict()
    kind = event['type']
    if kind in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
        if session.get('payment_status') == 'paid':
            _mark_paid(session)
    elif kind == 'checkout.session.expired':
        _mark_unpaid(session, 'expired')
    elif kind == 'checkout.session.async_payment_failed':
        _mark_unpaid(session, 'failed')


def _payment_for(session, lock=True):
    order_id = (session.get('metadata') or {}).get('order_id') or session.get('client_reference_id')
    if not order_id:
        return None
    queryset = Payment.objects.select_related('order', 'order__customer__user')
    if lock:
        queryset = queryset.select_for_update(of=('self',))
    return queryset.filter(order_id=order_id, payment_method=Payment.PaymentMethod.STRIPE).first()


def _mark_paid(session):
    from . import emails

    with transaction.atomic():
        payment = _payment_for(session)
        if payment is None or payment.status in (Payment.PaymentStatus.COMPLETED, Payment.PaymentStatus.REFUNDED):
            return
        if session.get('amount_total') != _cents(payment.amount):
            logger.error('Stripe amount %s does not match order %s (%s)',
                         session.get('amount_total'), payment.order.order_number, payment.amount)
        payment.transaction_id = session.get('payment_intent') or session['id']
        payment.payment_gateway_response = {
            'checkout_session': session['id'],
            'payment_intent': session.get('payment_intent'),
        }
        payment.save(update_fields=['transaction_id', 'payment_gateway_response', 'updated_at'])
        payment.complete_payment()
        order = payment.order

        if order.status == Order.StatusChoices.CANCELED:
            # Paid after the order was canceled: give the money back.
            refund(payment)
            return
        transaction.on_commit(lambda: emails.order_placed(order))


def _mark_unpaid(session, reason):
    from .services import OrderService

    with transaction.atomic():
        payment = _payment_for(session)
        if payment is None or payment.status != Payment.PaymentStatus.PENDING:
            return
        # Only the order's current payment page counts; an older page
        # expiring after the customer opened a new one changes nothing.
        if _session_info(payment).get('checkout_session') != session['id']:
            return
        payment.record_failure(f'Stripe checkout {reason}')
        order = payment.order
        if order.status == Order.StatusChoices.PENDING:
            with override(order.language):
                message = _('The online payment was not completed, so the order was canceled.')
            OrderService.update_order_status(order, Order.StatusChoices.CANCELED, reason=message)
