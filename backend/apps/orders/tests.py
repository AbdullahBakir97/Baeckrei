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
        OrderService.update_order_status(self.order, Order.StatusChoices.PROCESSING)
        OrderService.add_tracking_number(self.order, 'DHL123')
        OrderService.update_order_status(self.order, Order.StatusChoices.COMPLETED)
        self.assertEqual(self.order.status, Order.StatusChoices.COMPLETED)
