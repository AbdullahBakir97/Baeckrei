import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Address, Customer
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.core.testing import make_test_password

PASSWORD = make_test_password()

User = get_user_model()


def make_order(user):
    customer = Customer.objects.create(user=user, customer_id=uuid.uuid4().hex)
    address = Address.objects.create(
        customer=customer, address_line_1='Hauptstr. 1', city='Berlin',
        state='BE', postal_code='10115', country='DE',
    )
    return Order.objects.create(customer=customer, address=address)


class OrderPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(email='alice@example.com', password=PASSWORD)
        self.bob = User.objects.create_user(email='bob@example.com', password=PASSWORD)
        self.admin = User.objects.create_superuser(email='admin@example.com', password=PASSWORD)
        self.order = make_order(self.alice)
        self.bob_customer = Customer.objects.create(user=self.bob, customer_id=uuid.uuid4().hex)

    def url(self, suffix=''):
        return f'/api/orders/orders/{self.order.pk}/{suffix}'

    def test_customer_cannot_change_status_or_tracking(self):
        self.client.force_authenticate(self.alice)
        self.assertEqual(self.client.post(self.url('update_status/'), {'status': 'Processing'}).status_code, 403)
        self.assertEqual(self.client.post(self.url('add_tracking/'), {'tracking_number': 'X'}).status_code, 403)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.StatusChoices.PENDING)
        self.assertIsNone(self.order.shipping_tracking_number)

    def test_customer_cannot_reassign_or_restatus_via_patch(self):
        self.client.force_authenticate(self.alice)
        self.client.patch(self.url(), {'customer': self.bob_customer.pk, 'status': 'Completed'}, format='json')
        self.order.refresh_from_db()
        self.assertEqual(self.order.customer.user, self.alice)
        self.assertEqual(self.order.status, Order.StatusChoices.PENDING)

    def test_customer_cannot_delete_order(self):
        self.client.force_authenticate(self.alice)
        self.assertEqual(self.client.delete(self.url()).status_code, 403)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

    def test_other_customer_cannot_see_order(self):
        self.client.force_authenticate(self.bob)
        self.assertEqual(self.client.get(self.url()).status_code, 404)

    def test_owner_can_cancel_pending_order(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post(self.url('cancel/'))
        self.assertEqual(response.status_code, 200, response.content)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.StatusChoices.CANCELED)
        self.assertEqual(self.client.post(self.url('cancel/')).status_code, 400)

    def test_other_customer_cannot_cancel_order(self):
        self.client.force_authenticate(self.bob)
        self.assertEqual(self.client.post(self.url('cancel/')).status_code, 404)

    def test_staff_can_update_status(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url('update_status/'), {'status': 'Processing'})
        self.assertEqual(response.status_code, 200, response.content)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.StatusChoices.PROCESSING)


class OrderStatusTransitionTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(email='carol@example.com', password=PASSWORD)
        self.order = make_order(user)

    def test_cannot_reopen_canceled_order(self):
        OrderService.update_order_status(self.order, Order.StatusChoices.CANCELED)
        with self.assertRaises(ValueError):
            OrderService.update_order_status(self.order, Order.StatusChoices.PENDING)

    def test_cannot_skip_to_completed(self):
        with self.assertRaises(ValueError):
            OrderService.update_order_status(self.order, Order.StatusChoices.COMPLETED)

    def test_normal_flow(self):
        from decimal import Decimal
        from apps.orders.models import Payment
        payment = Payment.objects.create(order=self.order, payment_method='CA', amount=Decimal('1.00'))
        OrderService.update_order_status(self.order, Order.StatusChoices.PROCESSING)
        OrderService.update_order_status(self.order, Order.StatusChoices.COMPLETED)
        self.assertEqual(self.order.status, Order.StatusChoices.COMPLETED)
        # Cash is collected at handover, so completing the order marks it paid.
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PaymentStatus.COMPLETED)


class CheckoutTests(TestCase):
    def setUp(self):
        from decimal import Decimal
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.products.models import Category, Product

        self.client = APIClient()
        self.user = User.objects.create_user(email='dana@example.com', password='Str0ng-Passw0rd!')
        self.client.force_authenticate(self.user)
        category = Category.objects.create(name='Brot', description='Bread')
        self.bread = Product.objects.create(
            name='Roggenbrot', description='Rye', category=category, price=Decimal('3.50'),
            stock=5, status='active', available=True,
            image=SimpleUploadedFile('rye.png', b'\x89PNG', content_type='image/png'),
        )

    def _add(self, quantity):
        return self.client.post('/api/shopping-cart/add/', {'product_id': str(self.bread.id), 'quantity': quantity}, format='json')

    def _checkout(self, **overrides):
        payload = {'fulfillment_method': 'pickup', 'payment_method': 'CA'}
        payload.update(overrides)
        return self.client.post('/api/orders/orders/checkout/', payload, format='json')

    @classmethod
    def setUpClass(cls):
        import tempfile
        from django.test import override_settings
        cls._media_root = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        import shutil
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def test_pickup_checkout_creates_order_deducts_stock_and_closes_cart(self):
        from decimal import Decimal
        self.assertEqual(self._add(2).status_code, 200)
        response = self._checkout(notes='Please slice')
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data['fulfillment_method'], 'pickup')
        self.assertIsNone(data['address'])
        self.assertEqual(Decimal(data['total_price']), Decimal('7.00'))
        self.assertEqual(Decimal(data['vat_amount']), Decimal('1.12'))
        self.assertEqual(data['payment']['payment_method'], 'CA')
        self.assertEqual(data['items'][0]['quantity'], 2)
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock, 3)
        # The cart is closed; the next cart is empty.
        self.assertEqual(self.client.get('/api/shopping-cart/').json()['items'], [])

    def test_delivery_requires_address_and_adds_fee(self):
        from decimal import Decimal
        self._add(1)
        self.assertEqual(self._checkout(fulfillment_method='delivery').status_code, 400)
        response = self._checkout(fulfillment_method='delivery', payment_method='CC', address={
            'address_line_1': 'Friedrichstraße 1', 'city': 'Berlin', 'postal_code': '10117',
        })
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data['address']['city'], 'Berlin')
        self.assertEqual(Decimal(data['delivery_fee']), Decimal('3.50'))
        self.assertEqual(Decimal(data['total_price']), Decimal('7.00'))

    def test_saved_address_from_checkout_can_be_reused(self):
        self._add(1)
        response = self._checkout(fulfillment_method='delivery', save_address=True, address={
            'address_line_1': 'Unter den Linden 5', 'city': 'Berlin', 'postal_code': '10117',
        })
        self.assertEqual(response.status_code, 201, response.content)
        saved = self.client.get('/api/accounts/addresses/').json()
        self.assertEqual([a['address_line_1'] for a in saved], ['Unter den Linden 5'])
        self._add(1)
        response = self._checkout(fulfillment_method='delivery', address_id=saved[0]['id'])
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['address']['id'], saved[0]['id'])

    def test_paypal_is_rejected_until_configured(self):
        self._add(1)
        response = self._checkout(payment_method='PP')
        self.assertEqual(response.status_code, 400)
        self.assertIn('payment_method', response.json())

    def test_empty_cart_cannot_be_checked_out(self):
        response = self._checkout()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_type'], 'empty_cart')

    def test_checkout_fails_when_stock_ran_out_and_changes_nothing(self):
        self._add(3)
        self.bread.stock = 2  # someone else bought some in the meantime
        self.bread.save()
        response = self._checkout()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_type'], 'insufficient_stock')
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock, 2)
        self.assertFalse(Order.objects.filter(customer__user=self.user).exists())
        self.assertEqual(len(self.client.get('/api/shopping-cart/').json()['items']), 1)

    def test_canceling_returns_stock(self):
        self._add(2)
        order_id = self._checkout().json()['id']
        self.assertEqual(self.client.post(f'/api/orders/orders/{order_id}/cancel/').status_code, 200)
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock, 5)

    def test_checkout_options(self):
        data = self.client.get('/api/orders/orders/checkout_options/').json()
        self.assertEqual([m['code'] for m in data['fulfillment_methods']], ['pickup', 'delivery'])
        paypal = next(m for m in data['payment_methods'] if m['code'] == 'PP')
        self.assertFalse(paypal['available'])

    def test_customers_cannot_create_orders_directly(self):
        response = self.client.post('/api/orders/orders/', {}, format='json')
        self.assertEqual(response.status_code, 403)


class AdminOrderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email='boss@example.com', password='Str0ng-Passw0rd!')
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        alice = User.objects.create_user(email='alice@example.com', password='Str0ng-Passw0rd!')
        self.order = make_order(alice)

    def test_dashboard_stats_and_recent_orders(self):
        stats = self.client.get('/api/orders/orders/dashboard_stats/')
        self.assertEqual(stats.status_code, 200, stats.content)
        self.assertEqual(stats.json()['total_orders'], 1)
        self.assertEqual(stats.json()['open_orders'], 1)
        recent = self.client.get('/api/orders/orders/recent_orders/').json()
        self.assertEqual(recent[0]['customer_email'], 'alice@example.com')

    def test_filters(self):
        self.assertEqual(len(self.client.get('/api/orders/orders/', {'status': 'Pending'}).json()), 1)
        self.assertEqual(len(self.client.get('/api/orders/orders/', {'status': 'Completed'}).json()), 0)
        self.assertEqual(len(self.client.get('/api/orders/orders/', {'search': 'alice'}).json()), 1)
        self.assertEqual(len(self.client.get('/api/orders/orders/', {'search': 'nobody'}).json()), 0)
