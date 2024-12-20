from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from .controllers import CartController
from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging
import json

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for managing shopping carts."""
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.customer)

    def get_controller(self) -> CartController:
        """Get or create a CartController instance for the current cart."""
        cart = self.request.cart
        return CartController(cart.id)

    @extend_schema(
        description="Get the current cart",
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current cart."""
        try:
            controller = self.get_controller()
            response = controller.view_cart()
            logger.info(f"Current cart response: {response.content}")
            return Response(json.loads(response.content))
        except Exception as e:
            logger.error(f"Error getting current cart: {str(e)}")
            return Response(
                {'error': 'Error retrieving cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description="Add an item to the cart",
        request={'application/json': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'quantity': {'type': 'integer', 'minimum': 1}
            },
            'required': ['product_id']
        }},
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the cart."""
        try:
            controller = self.get_controller()
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))
            
            response = controller.add_item(product_id, quantity)
            logger.info(f"Add item response: {response.content}")
            data = json.loads(response.content)
            logger.info(f"Parsed response data: {data}")
            return Response(data)
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description="Remove an item from the cart",
        request={'application/json': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'}
            },
            'required': ['product_id']
        }},
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove an item from the cart."""
        try:
            controller = self.get_controller()
            product_id = request.data.get('product_id')
            
            response = controller.remove_item(product_id)
            logger.info(f"Remove item response: {response.content}")
            return Response(json.loads(response.content))
        except Exception as e:
            logger.error(f"Error removing item from cart: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description="Update cart item quantity",
        request={'application/json': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'quantity': {'type': 'integer', 'minimum': 1}
            },
            'required': ['product_id', 'quantity']
        }},
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update the quantity of an item in the cart."""
        try:
            controller = self.get_controller()
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))
            
            response = controller.update_quantity(product_id, quantity)
            logger.info(f"Update item response: {response.content}")
            return Response(json.loads(response.content))
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description="Clear the cart",
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from the cart."""
        try:
            controller = self.get_controller()
            response = controller.clear_cart()
            logger.info(f"Clear cart response: {response.content}")
            return Response(json.loads(response.content))
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )