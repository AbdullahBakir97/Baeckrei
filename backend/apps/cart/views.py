from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Cart
from .serializers import CartSerializer, CartDetailSerializer, CartOperationSerializer
from .controllers.CMC import CartManagementController
from apps.accounts.models import Customer
from .exceptions import CartException
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shopping carts.
    Supports both authenticated and guest users.
    """
    serializer_class = CartSerializer
    controller = CartManagementController()
    permission_classes = [AllowAny]  # Allow anonymous access by default

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action in ['retrieve', 'current']:
            return CartDetailSerializer
        return self.serializer_class

    @swagger_auto_schema(
        method='get',
        operation_summary="Get current cart",
        operation_description="Retrieve the current user's active shopping cart",
        responses={
            200: openapi.Response('Cart detail', CartDetailSerializer),
            404: openapi.Response('Cart not found'),
            400: openapi.Response('Validation error'),
            500: openapi.Response('Server error')
        }
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current cart for the user."""
        try:
            response = self.controller.view_cart(request)
            return response
        except CartException as e:
            logger.error(f"Cart error: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error getting current cart: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": "Failed to retrieve cart"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        method='post',
        operation_summary="Add item to cart",
        operation_description="Add a product to the shopping cart",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id', 'quantity'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response('Cart detail', CartDetailSerializer),
            400: openapi.Response('Invalid request data'),
            404: openapi.Response('Product not found')
        }
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart."""
        try:
            response = self.controller.add_item(request)
            return response
        except CartException as e:
            error_msg = str(e)
            if 'stock' in error_msg.lower():
                return Response(
                    {"status": "error", "detail": error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            logger.error(f"Cart error: {error_msg}", exc_info=True)
            return Response(
                {"status": "error", "detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": "Failed to add item to cart"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        method='put',
        operation_summary="Update cart item",
        operation_description="Update the quantity of an item in the cart",
        manual_parameters=[
            openapi.Parameter('product_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('quantity', openapi.IN_BODY, type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: openapi.Response('Cart detail', CartDetailSerializer),
            400: openapi.Response('Invalid request data'),
            404: openapi.Response('Product not found')
        }
    )
    @action(detail=False, methods=['put'])
    def update_item(self, request, product_id=None):
        """Update cart item quantity."""
        try:
            if not product_id:
                return Response(
                    {"status": "error", "detail": "Product ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            request._full_data = {
                'product_id': product_id,
                'quantity': request.data.get('quantity')
            }
            
            response = self.controller.update_item(request, product_id)
            return response
        except CartException as e:
            logger.error(f"Cart error: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='delete',
        operation_summary="Remove item from cart",
        operation_description="Remove an item from the shopping cart",
        manual_parameters=[
            openapi.Parameter('product_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: openapi.Response('Cart detail', CartDetailSerializer),
            400: openapi.Response('Invalid request data'),
            404: openapi.Response('Product not found')
        }
    )
    @action(detail=False, methods=['delete'])
    def remove_item(self, request, product_id=None):
        """Remove item from cart."""
        try:
            if not product_id:
                return Response(
                    {"status": "error", "detail": "Product ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            request._full_data = {'product_id': product_id}
            
            response = self.controller.remove_item(request, product_id)
            return response
        except CartException as e:
            logger.error(f"Cart error: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='post',
        operation_summary="Clear cart",
        operation_description="Remove all items from the shopping cart",
        responses={
            200: openapi.Response('Cart detail', CartDetailSerializer),
            400: openapi.Response('Invalid request')
        }
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart."""
        try:
            response = self.controller.clear_cart(request)
            return response
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
