from typing import Dict, Any, Optional, Tuple
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import Customer
from apps.cart.services.services import CartService
from apps.cart.services.cart_retriever import CartRetriever
from ..serializers import CartOperationSerializer, CartSerializer, CartDetailSerializer
from ..exceptions import (
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError,
    CartException
)
from django.core.exceptions import ValidationError
from ..models import Cart
from .base import BaseController
from .validators import CartRequestValidator
from .response_factory import CartResponseFactory
import logging
import uuid
from decimal import Decimal
from django.db import transaction

logger = logging.getLogger(__name__)

class CartManagementController(BaseController):
    """
    Controller for managing cart operations.
    Implements high-level business logic and coordinates between services.
    Follows SOLID principles and implements clean architecture patterns.
    """
    
    def __init__(self):
        """Initialize controller with dependencies."""
        super().__init__()
        self.cart_retriever = CartRetriever()
        self.response_factory = CartResponseFactory()
        self.validator = CartRequestValidator()

    def validate_request(self, request, required_fields=None, operation_type=None) -> Tuple[bool, Optional[Response], Optional[Dict]]:
        """Validate incoming request using CartRequestValidator."""
        return self.validator.validate_cart_operation(request, required_fields, operation_type)

    def _get_customer(self, request) -> Optional[Customer]:
        """Resolve the customer for an authenticated user (session or JWT)."""
        customer = getattr(request, 'customer', None)
        if customer:
            return customer
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None
        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={'customer_id': uuid.uuid4().hex},
        )
        return customer

    def get_or_create_cart(self, request) -> Tuple[Cart, bool]:
        """Get or create cart for the current session/user."""
        try:
            # request.user is resolved by DRF here, so JWT-authenticated users
            # get their customer cart rather than a per-session guest cart.
            customer = self._get_customer(request)

            if customer:
                # Signed in after shopping as a guest: bring the guest cart along.
                session_key = request.session.session_key
                if session_key and Cart.objects.filter(
                    session_key=session_key, customer__isnull=True, completed=False
                ).exists():
                    merged = self.cart_retriever.merge_guest_cart_to_customer(customer, session_key)
                    if merged:
                        self.cart_retriever.clear_cart_cache(session_key=session_key)
                        return merged, False
                cart, created = self.cart_retriever.get_or_create_for_customer(customer)
            else:
                if not request.session.session_key:
                    request.session.create()
                cart, created = self.cart_retriever.get_or_create_for_session(request.session.session_key)

            return cart, created

        except Exception as e:
            logger.error(f"Error in get_or_create_cart: {str(e)}")
            raise

    def merge_carts(self, guest_cart: Cart, user_cart: Cart) -> Cart:
        """Merge guest cart into user cart."""
        if not user_cart:
            guest_cart.customer = user_cart.customer
            guest_cart.session_key = None
            guest_cart.save()
            return guest_cart

        for item in guest_cart.items.all():
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        
        guest_cart.delete()
        return user_cart

    def handle_cart_merge(self, request) -> Optional[Cart]:
        """Handle merging guest cart into customer cart upon login."""
        try:
            user = getattr(request, '_cached_user', None) or request.user
            if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
                return None
                
            customer = getattr(request, 'customer', None)
            if not customer:
                customer = Customer.objects.filter(user=user).first()
                if customer:
                    request.customer = customer
                    
            if not customer:
                return None
                
            # Get guest cart by session key
            guest_cart = None
            if request.session.session_key:
                guest_cart = Cart.objects.filter(
                    session_key=request.session.session_key,
                    completed=False
                ).first()
                
            if not guest_cart:
                return None
                
            # Get or create customer cart
            customer_cart, created = Cart.objects.get_or_create(
                customer=customer,
                completed=False,
                defaults={'version': 1}
            )
            
            if not created and guest_cart.id == customer_cart.id:
                return customer_cart
                
            # Merge items
            with transaction.atomic():
                for item in guest_cart.items.all():
                    existing_item = customer_cart.items.filter(product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        if existing_item.quantity > item.product.stock:
                            existing_item.quantity = item.product.stock
                        existing_item.save()
                    else:
                        item.cart = customer_cart
                        item.save()
                
                guest_cart.delete()
                customer_cart.refresh_from_db()
                return customer_cart
                
        except Exception as e:
            logger.error(f"Error handling cart merge: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def _error_message(e: Exception) -> str:
        """Extract a readable message; CartService wraps details in a dict."""
        arg = e.args[0] if e.args else str(e)
        if isinstance(arg, dict):
            return arg.get('detail', {}).get('message') or arg.get('message') or str(arg)
        if isinstance(e, ValidationError):
            return '; '.join(e.messages)
        return str(arg)

    def handle_error(self, e: Exception, operation: str) -> Response:
        """Handle cart operation errors and return appropriate response."""
        if isinstance(e, CartAlreadyCheckedOutError):
            return self.response_factory.error_response(
                "Cart is already completed",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='cart_completed'
            )

        if isinstance(e, InsufficientStockError):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='insufficient_stock',
                extra_data={'available_stock': e.available_stock}
            )

        if isinstance(e, CartNotFoundError):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                error_type='cart_not_found'
            )

        if isinstance(e, (CartException, ValidationError)):
            arg = e.args[0] if e.args else None
            error_type = arg.get('code', 'cart_error') if isinstance(arg, dict) else 'cart_error'
            return self.response_factory.error_response(
                self._error_message(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type=error_type
            )

        logger.error(f"Error in {operation}: {str(e)}", exc_info=True)
        return self.response_factory.error_response(
            f"An error occurred during {operation}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type='operation_failed'
        )

    def _cart_response(self, request, cart: Cart) -> Response:
        """Serialize the cart freshly from the database."""
        cart = Cart.objects.select_related('customer').prefetch_related('items__product').get(id=cart.id)
        serializer = CartDetailSerializer(cart, context={'request': request})
        return self.response_factory.success_response(serializer.data)

    def view_cart(self, request) -> Response:
        """Get current cart details."""
        try:
            cart, _ = self.get_or_create_cart(request)
            return self._cart_response(request, cart)
        except Exception as e:
            return self.handle_error(e, 'view cart')

    def add_item(self, request) -> Response:
        """Add item to cart."""
        try:
            is_valid, error_response, validated_data = self.validate_request(
                request, ['product_id']
            )
            if not is_valid:
                return error_response

            cart, _ = self.get_or_create_cart(request)
            quantity = validated_data.get('quantity', 1)
            CartService().add_item(cart, validated_data['product_id'], quantity)
            request._cart_modified = True
            return self._cart_response(request, cart)
        except Exception as e:
            return self.handle_error(e, 'add item')

    def update_item(self, request, product_id) -> Response:
        """Set the quantity of a product that is already in the cart."""
        try:
            is_valid, error_response, validated_data = self.validate_request(
                request, required_fields=['quantity'], operation_type='update'
            )
            if not is_valid:
                return error_response

            cart, _ = self.get_or_create_cart(request)
            CartService().update_item(cart, product_id, validated_data['quantity'])
            request._cart_modified = True
            return self._cart_response(request, cart)
        except Exception as e:
            return self.handle_error(e, 'update item')

    def remove_item(self, request, product_id) -> Response:
        """Remove a product from the cart."""
        try:
            cart, _ = self.get_or_create_cart(request)
            CartService().remove_item(cart, product_id)
            request._cart_modified = True
            return self._cart_response(request, cart)
        except Exception as e:
            return self.handle_error(e, 'remove item')

    def clear_cart(self, request) -> Response:
        """Remove all items from the cart."""
        try:
            cart, _ = self.get_or_create_cart(request)
            CartService().clear(cart)
            request._cart_modified = True
            return self._cart_response(request, cart)
        except Exception as e:
            return self.handle_error(e, 'clear cart')
