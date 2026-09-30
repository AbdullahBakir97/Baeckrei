from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Customer

User = get_user_model()


class UserAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(email='alice@example.com', password='Str0ng-Passw0rd!')
        self.bob = User.objects.create_user(email='bob@example.com', password='Str0ng-Passw0rd!')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='Str0ng-Passw0rd!')

    def test_user_cannot_change_another_users_password(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch(f'/api/accounts/users/{self.admin.pk}/', {'password': 'hijacked-123!'})
        self.assertEqual(response.status_code, 404)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password('Str0ng-Passw0rd!'))

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
        response = self.client.patch('/api/accounts/users/me/', {'password': 'N3w-Passw0rd!'})
        self.assertEqual(response.status_code, 400)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password('Str0ng-Passw0rd!'))

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(self.alice)
        response = self.client.patch('/api/accounts/users/me/', {'first_name': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, 'Alice')

    def test_anonymous_cannot_create_users_through_generic_endpoint(self):
        response = self.client.post('/api/accounts/users/', {'email': 'x@example.com', 'password': 'Str0ng-Passw0rd!'})
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
            'password': 'Str0ng-Passw0rd!',
            'password2': 'Str0ng-Passw0rd!',
            'first_name': 'New',
            'last_name': 'User',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        user = User.objects.get(email='new@example.com')
        self.assertTrue(Customer.objects.filter(user=user).exists())
