"""Online payment (Stripe), order emails and slot validation at checkout."""
import hashlib
import hmac
import json
import shutil
import tempfile
import time
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

import stripe
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.core.testing import make_test_password
from apps.orders.models import Order, Payment
from apps.orders.slots import available_slots
from apps.products.models import Category, Product

User = get_user_model()
WEBHOOK_SECRET = 'whsec_test_secret'
STRIPE = dict(STRIPE_SECRET_KEY='sk_test_123', STRIPE_WEBHOOK_SECRET=WEBHOOK_SECRET, STRIPE_ENABLED=True)
SESSION = SimpleNamespace(id='cs_test_1', url='https://checkout.stripe.com/c/pay/cs_test_1', status='open')


def signed(payload):
    timestamp = int(time.time())
    signature = hmac.new(WEBHOOK_SECRET.encode(), f'{timestamp}.{payload}'.encode(), hashlib.sha256).hexdigest()
    return f't={timestamp},v1={signature}'


@override_settings(SHOP_NOTIFICATION_EMAIL='shop@example.com', SHOP_OPENING_HOURS='mon-sun 00:00-23:30',
                   SHOP_PICKUP_LEAD_MINUTES=60, SHOP_SLOT_CAPACITY=0)
class OrderFlowTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='mia@example.com', password=make_test_password(), first_name='Mia')
        self.client.force_authenticate(self.user)
        category = Category.objects.create(name='Brot', description='Bread')
        self.bread = Product.objects.create(
            name='Roggenbrot', name_en='Rye bread', description='Rye', category=category, price=Decimal('3.50'),
            stock=5, status='active', available=True,
            image=SimpleUploadedFile('rye.png', b'\x89PNG', content_type='image/png'),
        )

    def checkout(self, language='de', **overrides):
        self.client.post('/api/shopping-cart/add/', {'product_id': str(self.bread.id), 'quantity': 2}, format='json')
        payload = {'fulfillment_method': 'pickup', 'payment_method': 'CA', **overrides}
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post('/api/orders/orders/checkout/', payload, format='json', HTTP_ACCEPT_LANGUAGE=language)


class OrderEmailTests(OrderFlowTestCase):
    def test_cash_order_is_confirmed_by_email_in_the_shop_language(self):
        response = self.checkout(language='de')
        self.assertEqual(response.status_code, 201, response.content)
        number = response.json()['order_number']
        self.assertEqual(len(mail.outbox), 2)
        customer, shop = mail.outbox
        self.assertEqual(customer.to, ['mia@example.com'])
        self.assertIn(number, customer.subject)
        self.assertIn('Vielen Dank', customer.body)
        self.assertIn('2 × Roggenbrot', customer.body)
        self.assertIn('7,00 €', customer.body)
        self.assertIn('Vielen Dank', customer.alternatives[0][0])
        self.assertEqual(shop.to, ['shop@example.com'])
        self.assertIn('Neue Bestellung', shop.subject)

    def test_english_customers_get_english_email(self):
        self.checkout(language='en')
        customer = mail.outbox[0]
        self.assertIn('Thank you for your order', customer.body)
        self.assertIn('2 × Rye bread', customer.body)
        self.assertIn('€7.00', customer.body)
        self.assertEqual(Order.objects.get().language, 'en')

    def test_canceling_tells_the_customer(self):
        order_id = self.checkout().json()['id']
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(f'/api/orders/orders/{order_id}/cancel/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('storniert', mail.outbox[0].subject)

    @mock.patch('django.core.mail.EmailMultiAlternatives.send', side_effect=OSError('SMTP down'))
    def test_a_failing_mail_server_does_not_break_checkout(self, _send):
        self.assertEqual(self.checkout().status_code, 201)
        self.assertEqual(Order.objects.count(), 1)


class SlotCheckoutTests(OrderFlowTestCase):
    def test_a_listed_slot_can_be_booked(self):
        slot = available_slots('pickup')[0]['start']
        response = self.checkout(requested_time=slot.isoformat())
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Order.objects.get().requested_time, slot)

    def test_times_outside_the_slots_are_refused(self):
        off_grid = available_slots('pickup')[0]['start'] + timedelta(minutes=7)
        response = self.checkout(requested_time=off_grid.isoformat())
        self.assertEqual(response.status_code, 400)
        self.assertIn('requested_time', response.json())
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock, 5)

    def test_checkout_options_list_the_slots(self):
        data = self.client.get('/api/orders/orders/checkout_options/').json()
        first = data['slots']['pickup'][0]
        self.assertTrue(first['available'])
        self.assertGreater(timezone.datetime.fromisoformat(first['start']), timezone.now())


class StripeTests(OrderFlowTestCase):
    def test_online_payment_is_refused_until_configured(self):
        response = self.checkout(payment_method='ST')
        self.assertEqual(response.status_code, 400)
        self.assertIn('payment_method', response.json())

    @override_settings(**STRIPE)
    @mock.patch('stripe.checkout.Session.create', return_value=SESSION)
    def test_checkout_opens_a_stripe_payment_page_and_waits_for_payment(self, create):
        response = self.checkout(payment_method='ST', language='en')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['payment_url'], SESSION.url)
        # Nothing is confirmed before Stripe reports the payment.
        self.assertEqual(mail.outbox, [])
        payment = Payment.objects.get()
        self.assertEqual(payment.status, Payment.PaymentStatus.PENDING)
        self.assertEqual(payment.payment_gateway_response, {'checkout_session': 'cs_test_1'})

        params = create.call_args.kwargs
        self.assertEqual(params['locale'], 'en')
        self.assertEqual(params['customer_email'], 'mia@example.com')
        self.assertEqual(params['line_items'][0]['price_data']['product_data']['name'], 'Rye bread')
        total = sum(item['price_data']['unit_amount'] * item['quantity'] for item in params['line_items'])
        self.assertEqual(total, 700)
        self.assertTrue(params['success_url'].endswith(f'/orders/{payment.order_id}?placed=1&paid=1'))

    @override_settings(**STRIPE)
    @mock.patch('stripe.checkout.Session.create', side_effect=stripe.APIConnectionError('offline'))
    def test_order_is_kept_if_stripe_is_unreachable(self, _create):
        response = self.checkout(payment_method='ST')
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('payment_url', response.json())
        self.assertIn('payment_error', response.json())

    @override_settings(**STRIPE)
    @mock.patch('stripe.checkout.Session.retrieve', return_value=SESSION)
    @mock.patch('stripe.checkout.Session.create', return_value=SESSION)
    def test_pay_reopens_the_open_payment_page(self, create, _retrieve):
        order_id = self.checkout(payment_method='ST').json()['id']
        response = self.client.post(f'/api/orders/orders/{order_id}/pay/')
        self.assertEqual(response.json(), {'payment_url': SESSION.url})
        self.assertEqual(create.call_count, 1)

    # -- webhook ------------------------------------------------------------

    def webhook(self, kind, session):
        payload = json.dumps({'id': 'evt_1', 'object': 'event', 'type': kind, 'data': {'object': session}})
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post('/api/orders/payments/stripe/webhook/', payload, content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE=signed(payload))

    def placed_online(self):
        with mock.patch('stripe.checkout.Session.create', return_value=SESSION):
            order = Order.objects.get(pk=self.checkout(payment_method='ST').json()['id'])
        return order, {
            'id': 'cs_test_1', 'object': 'checkout.session', 'payment_status': 'paid', 'amount_total': 700,
            'payment_intent': 'pi_test_1', 'client_reference_id': str(order.pk), 'metadata': {'order_id': str(order.pk)},
        }

    @override_settings(**STRIPE)
    def test_paid_webhook_marks_the_payment_and_sends_the_confirmation(self):
        order, session = self.placed_online()
        self.assertEqual(self.webhook('checkout.session.completed', session).status_code, 200)
        payment = Payment.objects.get()
        self.assertEqual(payment.status, Payment.PaymentStatus.COMPLETED)
        self.assertEqual(payment.transaction_id, 'pi_test_1')
        self.assertEqual(len(mail.outbox), 2)
        # Stripe retries webhooks; a second delivery changes nothing.
        self.webhook('checkout.session.completed', session)
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(**STRIPE)
    def test_webhook_rejects_bad_signatures(self):
        order, session = self.placed_online()
        payload = json.dumps({'type': 'checkout.session.completed', 'data': {'object': session}})
        response = self.client.post('/api/orders/payments/stripe/webhook/', payload, content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE='t=1,v1=forged')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.get().status, Payment.PaymentStatus.PENDING)

    @override_settings(**STRIPE)
    def test_expired_payment_page_cancels_the_order_and_frees_the_stock(self):
        order, session = self.placed_online()
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock, 3)
        self.webhook('checkout.session.expired', {**session, 'payment_status': 'unpaid'})
        order.refresh_from_db()
        self.bread.refresh_from_db()
        self.assertEqual(order.status, Order.StatusChoices.CANCELED)
        self.assertEqual(order.order_payment.status, Payment.PaymentStatus.FAILED)
        self.assertEqual(self.bread.stock, 5)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('nicht abgeschlossen', mail.outbox[0].body)

    @override_settings(**STRIPE)
    def test_an_old_payment_page_expiring_is_ignored(self):
        order, session = self.placed_online()
        self.webhook('checkout.session.expired', {**session, 'id': 'cs_old', 'payment_status': 'unpaid'})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.StatusChoices.PENDING)

    @override_settings(**STRIPE)
    @mock.patch('stripe.Refund.create')
    def test_canceling_a_paid_order_refunds_it(self, refund):
        order, session = self.placed_online()
        self.webhook('checkout.session.completed', session)
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(f'/api/orders/orders/{order.pk}/cancel/')
        self.assertEqual(response.status_code, 200)
        refund.assert_called_once()
        self.assertEqual(refund.call_args.kwargs['payment_intent'], 'pi_test_1')
        self.assertEqual(Payment.objects.get().status, Payment.PaymentStatus.REFUNDED)
        self.assertIn('erstattet', mail.outbox[0].body)

    @override_settings(**STRIPE)
    @mock.patch('stripe.Refund.create', side_effect=stripe.APIConnectionError('offline'))
    def test_order_stays_if_the_refund_fails(self, _refund):
        order, session = self.placed_online()
        self.webhook('checkout.session.completed', session)
        response = self.client.post(f'/api/orders/orders/{order.pk}/cancel/')
        self.assertEqual(response.status_code, 400)
        order.refresh_from_db()
        self.bread.refresh_from_db()
        self.assertEqual(order.status, Order.StatusChoices.PENDING)
        self.assertEqual(self.bread.stock, 3)
        self.assertEqual(Payment.objects.get().status, Payment.PaymentStatus.COMPLETED)

    @override_settings(**STRIPE)
    @mock.patch('stripe.checkout.Session.expire')
    def test_canceling_before_paying_closes_the_payment_page(self, expire):
        order, _session = self.placed_online()
        self.client.post(f'/api/orders/orders/{order.pk}/cancel/')
        expire.assert_called_once_with('cs_test_1', api_key='sk_test_123')
        self.assertEqual(Payment.objects.get().status, Payment.PaymentStatus.FAILED)
