import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from apps.cart.models import Cart, CartItem
from apps.products.models import Product

@pytest.mark.django_db
class TestCartErrorHandling:
    """Test error handling scenarios for cart operations."""

    def test_invalid_product_id(self, authenticated_client):
        """Test handling of invalid product IDs."""
        url = reverse('cart:add-to-cart')
        
        response = authenticated_client.post(url, {
            'product_id': '99999',
            'quantity': 1
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'invalid product id' in str(response.data).lower()

    def test_invalid_quantity(self, authenticated_client, active_product):
        """Test handling of invalid quantities."""
        url = reverse('cart:add-to-cart')
        
        # Test negative quantity
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': -1
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'quantity must be at least 1' in str(response.data).lower()
        
        # Test zero quantity
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 0
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'quantity must be at least 1' in str(response.data).lower()

    def test_exceed_stock_limit(self, authenticated_client, active_product):
        """Test handling of stock limit violations."""
        url = reverse('cart:add-to-cart')
        exceed_quantity = active_product.stock + 1
        
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': exceed_quantity
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'exceeds available stock' in str(response.data).lower()

    def test_add_to_completed_cart(self, authenticated_client, active_product, test_cart):
        """Test adding item to a completed cart."""
        url = reverse('cart:add-to-cart')
        
        # Mark cart as completed
        test_cart.completed = True
        test_cart.save()
        
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 1
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cart is already completed' in str(response.data).lower()

    def test_product_availability(self, authenticated_client, active_product):
        """Test handling of product availability changes."""
        url = reverse('cart:add-to-cart')
        
        # First add the product while it's available
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 1
        })
        assert response.status_code == status.HTTP_200_OK
        
        # Make product unavailable
        active_product.available = False
        active_product.save()
        
        # Try to add more of the unavailable product
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 1
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not available' in str(response.data).lower()

    def test_malformed_request(self, authenticated_client, active_product):
        """Test handling of malformed requests."""
        url = reverse('cart:add-to-cart')
        
        # Missing quantity
        response = authenticated_client.post(url, {
            'product_id': active_product.id
        })
        assert response.status_code == status.HTTP_200_OK  # Default quantity is 1
        
        # Invalid quantity type
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 'not_a_number'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'invalid' in str(response.data).lower()

    def test_concurrent_stock_updates(self, authenticated_client, active_product):
        """Test handling of concurrent stock updates."""
        url = reverse('cart:add-to-cart')
        
        # Add item to cart
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 2
        })
        assert response.status_code == status.HTTP_200_OK
        
        # Simulate stock reduction from another transaction
        active_product.stock = 1
        active_product.save()
        
        # Try to update quantity
        response = authenticated_client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': active_product.id}),
            {'quantity': 3}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'exceeds available stock' in str(response.data).lower()

    def test_invalid_cart_operations(self, authenticated_client, active_product):
        """Test handling of invalid cart operations."""
        # Try to update non-existent cart item
        response = authenticated_client.put(
            reverse('cart:update-cart-item', kwargs={'product_id': active_product.id}),
            {'quantity': 1}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not found in cart' in str(response.data).lower()
        
        # Try to remove non-existent cart item
        response = authenticated_client.delete(
            reverse('cart:remove-from-cart', kwargs={'product_id': active_product.id})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not found in cart' in str(response.data).lower()

    def test_session_handling_errors(self, authenticated_client):
        """Test handling of session-related errors."""
        # Test with invalid session key
        authenticated_client.cookies['sessionid'] = 'invalid_session_key'
        response = authenticated_client.get(reverse('cart:cart-detail'))
        assert response.status_code == status.HTTP_200_OK  # Should create new session
        assert 'cart' in str(response.data).lower()

    def test_cart_state_validation(self, authenticated_client, active_product, test_cart):
        """Test validation of cart state transitions."""
        url = reverse('cart:add-to-cart')
        
        # Mark cart as completed
        test_cart.completed = True
        test_cart.save()
        
        response = authenticated_client.post(url, {
            'product_id': active_product.id,
            'quantity': 1
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cart is already completed' in str(response.data).lower()