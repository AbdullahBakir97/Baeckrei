from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Customer
from apps.core.testing import make_test_password

PASSWORD = make_test_password()
NEW_PASSWORD = make_test_password()

User = get_user_model()


class UserAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(email='alice@example.com', password=PASSWORD)
        self.bob = User.objects.create_user(email='bob@example.com', password=PASSWORD)
        self.admin = User.objects.create_superuser(email='admin@example.com', password=PASSWORD)

    def test_user_cannot_change_another_users_password(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch(f'/api/accounts/users/{self.admin.pk}/', {'password': make_test_password()})
        self.assertEqual(response.status_code, 404)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(PASSWORD))

    def test_user_cannot_delete_or_deactivate_other_accounts(self):
        self.client.force_authenticate(self.alice)
        self.assertIn(self.client.delete(f'/api/accounts/users/{self.bob.pk}/').status_code, (403, 404))
        self.client.patch(f'/api/accounts/users/{self.alice.pk}/', {'is_active': False})
        self.bob.refresh_from_db()
        self.alice.refresh_from_db()
        self.assertTrue(self.bob.is_active)
        self.assertTrue(self.alice.is_active)

    def test_user_list_only_contains_self_for_non_staff(self):
        self.client.force_authenticate(self.alice)
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([u['email'] for u in response.json()], ['alice@example.com'])

    def test_password_cannot_be_changed_through_profile_update(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch('/api/accounts/users/me/', {'password': make_test_password()})
        self.assertEqual(response.status_code, 400)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password(PASSWORD))

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch('/api/accounts/users/me/', {'first_name': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, 'Alice')

    def test_anonymous_cannot_create_users_through_generic_endpoint(self):
        response = self.client.post('/api/accounts/users/', {'email': 'x@example.com', 'password': PASSWORD})
        self.assertEqual(response.status_code, 401)
        self.assertFalse(User.objects.filter(email='x@example.com').exists())

    def test_staff_can_list_all_users(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)


class RegisterTests(TestCase):
    def test_register_creates_user_and_customer(self):
        response = APIClient().post('/api/accounts/users/register/', {
            'email': 'new@example.com',
            'password': PASSWORD,
            'password2': PASSWORD,
            'first_name': 'New',
            'last_name': 'User',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        user = User.objects.get(email='new@example.com')
        self.assertTrue(Customer.objects.filter(user=user).exists())


class AddressTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(email='alice@example.com', password=PASSWORD)
        self.bob = User.objects.create_user(email='bob@example.com', password=PASSWORD)
        self.client.force_authenticate(self.alice)

    def _create(self, **extra):
        payload = {'address_line_1': 'Friedrichstraße 1', 'city': 'Berlin', 'postal_code': '10117'}
        payload.update(extra)
        return self.client.post('/api/accounts/addresses/', payload, format='json')

    def test_create_list_update_delete(self):
        response = self._create()
        self.assertEqual(response.status_code, 201, response.content)
        address_id = response.json()['id']
        self.assertEqual(response.json()['country'], 'DE')
        self.assertEqual(len(self.client.get('/api/accounts/addresses/').json()), 1)
        response = self.client.patch(f'/api/accounts/addresses/{address_id}/', {'city': 'Potsdam'}, format='json')
        self.assertEqual(response.json()['city'], 'Potsdam')
        self.assertEqual(self.client.delete(f'/api/accounts/addresses/{address_id}/').status_code, 204)
        self.assertEqual(self.client.get('/api/accounts/addresses/').json(), [])

    def test_addresses_are_private(self):
        address_id = self._create().json()['id']
        other = APIClient()
        other.force_authenticate(self.bob)
        self.assertEqual(other.get('/api/accounts/addresses/').json(), [])
        self.assertEqual(other.delete(f'/api/accounts/addresses/{address_id}/').status_code, 404)

    def test_deleting_an_address_used_by_an_order_only_hides_it(self):
        from apps.accounts.models import Address
        from apps.orders.models import Order
        address_id = self._create().json()['id']
        address = Address.objects.get(pk=address_id)
        Order.objects.create(customer=address.customer, address=address, fulfillment_method='delivery')
        self.assertEqual(self.client.delete(f'/api/accounts/addresses/{address_id}/').status_code, 204)
        self.assertEqual(self.client.get('/api/accounts/addresses/').json(), [])
        self.assertTrue(Address.objects.filter(pk=address_id).exists())


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='carol@example.com', password=PASSWORD)

    def test_reset_flow(self):
        import re
        from django.core import mail
        response = APIClient().post('/api/accounts/password-reset/', {'email': 'carol@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        uid, token = re.search(r'/reset-password/([^/]+)/(\S+)', mail.outbox[0].body).groups()
        response = APIClient().post('/api/accounts/password-reset/confirm/', {
            'uid': uid, 'token': token, 'new_password': NEW_PASSWORD,
        })
        self.assertEqual(response.status_code, 200, response.content)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        # The link only works once.
        response = APIClient().post('/api/accounts/password-reset/confirm/', {
            'uid': uid, 'token': token, 'new_password': make_test_password(),
        })
        self.assertEqual(response.status_code, 400)

    def test_unknown_email_gets_same_answer_and_no_mail(self):
        from django.core import mail
        response = APIClient().post('/api/accounts/password-reset/', {'email': 'nobody@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_token_is_rejected(self):
        response = APIClient().post('/api/accounts/password-reset/confirm/', {
            'uid': 'MQ', 'token': 'bad-token', 'new_password': NEW_PASSWORD,
        })
        self.assertEqual(response.status_code, 400)

    def test_requests_are_rate_limited(self):
        client = APIClient()
        codes = [client.post('/api/accounts/password-reset/', {'email': 'x@example.com'}).status_code for _ in range(6)]
        self.assertEqual(codes[-1], 429)


class AdminUserTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email='boss@example.com', password=PASSWORD)
        self.alice = User.objects.create_user(email='alice@example.com', password=PASSWORD, first_name='Alice')
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_search_and_order_count(self):
        users = self.client.get('/api/accounts/users/', {'search': 'alice'}).json()
        self.assertEqual([u['email'] for u in users], ['alice@example.com'])
        self.assertEqual(users[0]['order_count'], 0)

    def test_staff_can_deactivate_and_promote(self):
        response = self.client.patch(f'/api/accounts/users/{self.alice.pk}/', {'is_active': False, 'is_staff': True}, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        self.alice.refresh_from_db()
        self.assertFalse(self.alice.is_active)
        self.assertTrue(self.alice.is_staff and self.alice.is_admin)

    def test_staff_cannot_lock_themselves_out(self):
        response = self.client.patch(f'/api/accounts/users/{self.admin.pk}/', {'is_active': False}, format='json')
        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_accounts_dashboard_stats(self):
        response = self.client.get('/api/accounts/users/dashboard_stats/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total_users'], 2)
