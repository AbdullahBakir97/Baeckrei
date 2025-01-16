from django.http import JsonResponse
from typing import Dict, Any, Optional
from .services import CartService
from products.models import Product
from .exceptions import (
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError,
    EmptyCartError,
    InvalidCouponError,
    CouponAlreadyAppliedError
)
import logging

logger = logging.getLogger(__name__)

class CartController:
    """Controller to handle cart-related operations."""

    def __init__(self, cart_id: int):
        """Initialize the CartController with a CartService instance."""
        try:
            self.cart_service = CartService(cart_id)
            # Initialize command mapping
            self._commands = {
                'add': lambda pid, qty: self.add_item(pid, qty or 1),
                'remove': self.remove_item,
                'update': self.update_quantity,
                'clear': self.clear_cart,
                'view': lambda details, _: self.view_cart(details) 
            }
            logger.info(f"CartController initialized for cart {cart_id}")
        except CartNotFoundError:
            logger.error(f"Cart not found: {cart_id}")
            raise CartNotFoundError(cart_id)
        except CartAlreadyCheckedOutError as e:
            logger.error(f"Cart already checked out: {cart_id}")
            raise CartAlreadyCheckedOutError(str(e))

    def handle_error(self, exception: Exception) -> JsonResponse:
        """Standardized error response for cart-related operations."""
        error_mapping = {
            InvalidQuantityError: {
                'error': 'Invalid quantity',
                'detail': lambda e: f"Invalid quantity: {e.quantity}. Quantity must be greater than 0.",
                'status': 400,
                'extra': lambda e: {'provided_quantity': e.quantity}
            },
            InsufficientStockError: {
                'error': 'Insufficient stock',
                'detail': lambda e: (f"Not enough stock available for {e.item}. "
                                   f"Required: {e.required_quantity}, Available: {e.available_stock}"),
                'status': 400,
                'extra': lambda e: {
                    'item': e.item,
                    'required': e.required_quantity,
                    'available': e.available_stock
                }
            },
            CartNotFoundError: {
                'error': 'Cart not found',
                'detail': lambda e: f"Cart with ID {e.cart_id} not found.",
                'status': 404,
                'extra': lambda e: {'cart_id': e.cart_id}
            },
            CartAlreadyCheckedOutError: {
                'error': 'Cart already checked out',
                'detail': lambda e: str(e),
                'status': 400,
                'extra': None
            },
            EmptyCartError: {
                'error': 'Empty cart',
                'detail': lambda e: "Cannot proceed with an empty cart.",
                'status': 400,
                'extra': None
            },
            InvalidCouponError: {
                'error': 'Invalid coupon',
                'detail': lambda e: f"The coupon code '{e.coupon_code}' is not valid.",
                'status': 400,
                'extra': lambda e: {'coupon_code': e.coupon_code}
            },
            CouponAlreadyAppliedError: {
                'error': 'Coupon already applied',
                'detail': lambda e: f"The coupon '{e.coupon_code}' has already been applied to this cart.",
                'status': 400,
                'extra': lambda e: {'coupon_code': e.coupon_code}
            }
        }
        
        error_info = error_mapping.get(type(exception), {
            'error': 'Unexpected error',
            'detail': lambda e: str(e),
            'status': 500,
            'extra': None
        })

        response_data = {
            'error': error_info['error'],
            'detail': error_info['detail'](exception)
        }

        if error_info['extra']:
            response_data['extra'] = error_info['extra'](exception)

        logger.error(f"Cart operation error: {response_data['error']} - {response_data['detail']}")
        return JsonResponse(response_data, status=error_info['status'])

    def modify_cart(self, action: str, product_id: Optional[int] = None, 
                   quantity: Optional[int] = None) -> JsonResponse:
        """Execute cart modifications using command pattern with direct method references."""
        try:
            command = self._commands.get(action)
            if not command:
                logger.error(f"Invalid cart action attempted: {action}")
                return JsonResponse({
                    'error': 'Invalid action',
                    'detail': f'The action "{action}" is not supported.'
                }, status=400)

            logger.info(f"Executing cart action: {action} for cart {self.cart_service.cart.id}")
            if product_id:
                logger.info(f"Product ID: {product_id}, Quantity: {quantity}")
            
            # Execute the command
            result = command(product_id, quantity)
            
            # Ensure we return fresh cart data after modifications
            cart_data = self.cart_service.get_cart_data(include_details=True)
            logger.info(f"Cart operation response: {cart_data}")
            return JsonResponse(cart_data)

        except (InvalidQuantityError, InsufficientStockError, 
                CartAlreadyCheckedOutError, CartNotFoundError, 
                EmptyCartError, InvalidCouponError, CouponAlreadyAppliedError) as e:
            return self.handle_error(e)
        except Exception as e:
            logger.exception(f"Unexpected error during cart operation: {str(e)}")
            return JsonResponse({
                'error': 'Server error',
                'detail': 'An unexpected error occurred. Please try again later.'
            }, status=500)

    def add_item(self, product_id: int, quantity: int = 1) -> JsonResponse:
        logger.info(f"Adding item: product_id={product_id}, quantity={quantity}")
        return self.modify_cart("add", product_id, quantity)

    def remove_item(self, product_id: int) -> JsonResponse:
        logger.info(f"Removing item: product_id={product_id}")
        return self.modify_cart("remove", product_id)

    def update_quantity(self, product_id: int, quantity: int) -> JsonResponse:
        logger.info(f"Updating quantity: product_id={product_id}, quantity={quantity}")
        return self.modify_cart("update", product_id, quantity)

    def clear_cart(self) -> JsonResponse:
        logger.info("Clearing cart")
        return self.modify_cart("clear")

    def view_cart(self, include_details: bool = True) -> JsonResponse:
        """Retrieve the cart's data with configurable detail level."""
        try:
            response_data = self.cart_service.get_cart_data(include_details)
            logger.info(f"View cart response: {response_data}")
            return JsonResponse(response_data)
        except Exception as e:
            logger.exception(f"Error viewing cart: {str(e)}")
            return JsonResponse({
                'error': 'Error viewing cart',
                'detail': str(e)
            }, status=400)
