from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.verify_url = reverse('token_verify')

    def test_user_can_login(self):
        """Test user can login and receive JWT tokens"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_can_refresh_token(self):
        """Test user can refresh JWT token"""
        # First, get tokens
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        refresh_token = response.data['refresh']

        # Then, use refresh token to get new access token
        response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_login(self):
        """Test invalid login credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_token(self):
        """Test token verification"""
        # First, get tokens
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        token = response.data['access']

        # Verify the token
        response = self.client.post(self.verify_url, {
            'token': token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_invalid_token(self):
        """Test invalid token verification"""
        response = self.client.post(self.verify_url, {
            'token': 'invalid-token'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
