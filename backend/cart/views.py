from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from .controllers import CartController
from .exceptions import (
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError,
    EmptyCartError
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging
import json
from functools import wraps

logger = logging.getLogger(__name__)

def handle_cart_action(action_name: str):
    """Decorator for handling cart actions with consistent error handling and logging."""
    def decorator(func):
        @wraps(func)
        def wrapper(viewset, request, *args, **kwargs):
            try:
                logger.info(f"Executing cart action: {action_name}")
                logger.info(f"Request data: {request.data}")
                
                result = func(viewset, request, *args, **kwargs)
                
                if isinstance(result, tuple):
                    response_data, extra_logs = result
                    for log in extra_logs:
                        logger.info(log)
                else:
                    response_data = result
                
                if isinstance(response_data, (Response,)):
                    return response_data
                    
                logger.info(f"Cart action {action_name} completed successfully")
                return Response(response_data)
                
            except (InvalidQuantityError, InsufficientStockError) as e:
                logger.warning(f"Validation error in {action_name}: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except CartNotFoundError as e:
                logger.error(f"Cart not found in {action_name}: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            except CartAlreadyCheckedOutError as e:
                logger.error(f"Cart already checked out in {action_name}: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ValueError as e:
                logger.warning(f"Invalid value in {action_name}: {str(e)}")
                return Response(
                    {'error': 'Invalid value provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.exception(f"Unexpected error in {action_name}: {str(e)}")
                return Response(
                    {'error': 'An unexpected error occurred'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator

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
    @handle_cart_action("view_cart")
    def current(self, request):
        """Get the current cart."""
        controller = self.get_controller()
        response = controller.view_cart()
        return json.loads(response.content)

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
    @handle_cart_action("add_item")
    def add_item(self, request):
        """Add an item to the cart."""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            raise InvalidQuantityError(quantity)
            
        controller = self.get_controller()
        response = controller.add_item(product_id, quantity)
        return json.loads(response.content)

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
    @handle_cart_action("update_item")
    def update_item(self, request):
        """Update the quantity of an item in the cart."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not product_id or not quantity:
            raise ValueError('Both product_id and quantity are required')
        
        quantity = int(quantity)
        if quantity <= 0:
            raise InvalidQuantityError(quantity)
            
        controller = self.get_controller()
        response = controller.update_quantity(product_id, quantity)
        return json.loads(response.content)

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
    @handle_cart_action("remove_item")
    def remove_item(self, request):
        """Remove an item from the cart."""
        product_id = request.data.get('product_id')
        if not product_id:
            raise ValueError('product_id is required')
            
        controller = self.get_controller()
        response = controller.remove_item(product_id)
        return json.loads(response.content)

    @extend_schema(
        description="Clear the cart",
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'])
    @handle_cart_action("clear_cart")
    def clear(self, request):
        """Clear all items from the cart."""
        controller = self.get_controller()
        response = controller.clear_cart()
        return json.loads(response.content)
