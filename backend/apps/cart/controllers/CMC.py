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

    def get_or_create_cart(self, request) -> Tuple[Cart, bool]:
        """Get or create cart for the current session/user."""
        try:
            # Get customer from request (set by CustomerMiddleware)
            customer = getattr(request, 'customer', None)
            user = getattr(request, '_cached_user', None) or request.user
            
            # Get session key, creating if needed
            if not request.session.session_key:
                request.session.create()
                
            if user and not isinstance(user, AnonymousUser) and user.is_authenticated and customer:
                # For authenticated users, get or create cart by customer
                cart, created = self.cart_retriever.get_or_create_for_customer(customer)
            else:
                # For anonymous users, get or create cart by session
                cart, created = self.cart_retriever.get_or_create_for_session(request.session.session_key)
                
            # Ensure cart is properly loaded with all relationships
            if cart:
                cart = Cart.objects.select_related('customer').prefetch_related('items').get(id=cart.id)
                
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

    def handle_error(self, e: Exception, operation: str) -> Response:
        """Handle cart operation errors and return appropriate response."""
        if isinstance(e, CartAlreadyCheckedOutError):
            return self.response_factory.error_response(
                "Cart is already completed",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='cart_completed'
            )
            
        elif isinstance(e, InvalidQuantityError):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='invalid_quantity'
            )
            
        elif isinstance(e, InsufficientStockError):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='insufficient_stock',
                extra_data={'available_stock': e.available_stock}
            )
            
        elif isinstance(e, CartNotFoundError):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                error_type='cart_not_found'
            )
            
        elif isinstance(e, CartException):
            return self.response_factory.error_response(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='cart_error'
            )
            
        logger.error(f"Error in {operation}: {str(e)}")
        return self.response_factory.error_response(
            f"An error occurred during {operation}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type='operation_failed'
        )

    def view_cart(self, request) -> Response:
        """Get current cart details."""
        try:
            cart, _ = self.get_or_create_cart(request)
            
            # Ensure cart is properly loaded with all relationships
            cart = Cart.objects.select_related('customer').prefetch_related('items').get(id=cart.id)
            
            serializer = CartDetailSerializer(cart, context={'request': request})
            return self.response_factory.create_success_response(
                serializer.data,
                "Cart retrieved successfully"
            )
        except Exception as e:
            return self.handle_error(e, 'view cart')

    def add_item(self, request) -> Response:
        """Add item to cart."""
        try:
            # Validate request data
            is_valid, error_response, validated_data = self.validate_request(
                request, ['product_id']
            )
            if not is_valid:
                return error_response

            # Get cart and product ID
            cart, _ = self.get_or_create_cart(request)
            product_id = validated_data.get('product_id')

            # Validate product ID format
            try:
                uuid.UUID(str(product_id))
            except (ValueError, AttributeError, TypeError):
                return self.response_factory.create_error_response(
                    ValidationError("Invalid product ID"),
                    "Invalid product ID format. Must be a valid UUID."
                )

            # Get quantity with default value
            quantity = int(validated_data.get('quantity', 1))
            if quantity <= 0:
                return self.response_factory.create_error_response(
                    InvalidQuantityError("Quantity must be greater than 0"),
                    "Quantity must be greater than 0"
                )

            # Initialize cart service and add item
            try:
                cart_service = CartService(cart)
                
                # Check stock availability
                product = Product.objects.get(id=product_id)
                if quantity > product.stock:
                    return self.response_factory.create_error_response(
                        InsufficientStockError(f"Insufficient stock. Available: {product.stock}"),
                        f"Insufficient stock. Only {product.stock} items available."
                    )
                
                cart_service.add_item(product_id, quantity)
                
                # Mark cart as modified for middleware
                request._cart_modified = True
                
                # Ensure cart is properly loaded with all relationships
                cart = Cart.objects.select_related('customer').prefetch_related('items').get(id=cart.id)
                
                # Serialize the updated cart
                serializer = CartDetailSerializer(cart)
                return self.response_factory.create_success_response(
                    serializer.data,
                    "Item added to cart successfully"
                )
                
            except CartNotFoundError as e:
                return self.response_factory.create_error_response(
                    e,
                    "Product not found"
                )
            except InsufficientStockError as e:
                return self.response_factory.create_error_response(
                    e,
                    str(e)
                )
            except CartException as e:
                return self.response_factory.create_error_response(
                    e,
                    str(e)
                )
            except ValidationError as e:
                return self.response_factory.create_error_response(
                    e,
                    str(e)
                )

        except Exception as e:
            return self.handle_error(e, 'add item')

    def remove_item(self, request, product_id: str) -> Response:
        """Remove item from cart."""
        try:
            # Get product_id from URL kwargs
            if not product_id:
                return self.response_factory.create_error_response(
                    ValidationError("Product ID is required"),
                    "Product ID is required"
                )

            cart, _ = self.get_or_create_cart(request)
            cart_service = CartService(cart)
            
            try:
                result = cart_service.remove_item(product_id)
                return self.response_factory.create_success_response(
                    result,
                    "Item removed from cart successfully"
                )
            except CartException as e:
                return self.response_factory.create_error_response(e, str(e))
            except ValidationError as e:
                return self.response_factory.create_error_response(e, str(e))

        except Exception as e:
            return self.handle_error(e, 'remove item')

    def update_item(self, request, product_id: str) -> Response:
        """Update item quantity in cart."""
        try:
            # Validate request data (only quantity is required in body)
            is_valid, error_response, validated_data = self.validate_request(
                request,
                required_fields=['quantity'],
                operation_type='update'
            )
            if not is_valid:
                return error_response

            cart, _ = self.get_or_create_cart(request)
            cart_service = CartService(cart)
            
            quantity = validated_data['quantity']
            
            try:
                result = cart_service.update_item(product_id, quantity)
                return self.response_factory.create_success_response(
                    result,
                    "Cart item updated successfully"
                )
            except CartException as e:
                return self.response_factory.create_error_response(e, str(e))
            except ValidationError as e:
                return self.response_factory.create_error_response(e, str(e))

        except Exception as e:
            return self.handle_error(e, 'update item')

    def clear_cart(self, request):
        """Clear all items from cart."""
        try:
            cart, _ = self.get_or_create_cart(request)
            
            # Initialize cart service and clear items
            cart_service = CartService(cart)
            result = cart_service.clear()
            
            # Mark cart as modified for middleware
            request._cart_modified = True
            
            # Ensure cart is properly loaded with all relationships
            cart = Cart.objects.select_related('customer').prefetch_related('items').get(id=cart.id)
            
            # Serialize the updated cart
            serializer = CartDetailSerializer(cart)
            return self.response_factory.create_success_response(
                serializer.data,
                "Cart cleared successfully"
            )
        except Exception as e:
            return self.handle_error(e, 'clear cart')
