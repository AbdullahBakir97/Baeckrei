from django.http import JsonResponse
from typing import Dict, Any, Optional
from .services import CartService
from products.models import Product
from .exceptions import (
    CartNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
    CartAlreadyCheckedOutError
)
import logging

logger = logging.getLogger(__name__)

class CartController:
    """Controller to handle cart-related operations."""

    def __init__(self, cart_id: int):
        """Initialize the CartController with a CartService instance."""
        try:
            self.cart_service = CartService(cart_id)
            # Initialize command mapping using lambdas
            self._commands = {
                'add': lambda pid, qty: self.cart_service.add_item(pid, qty),
                'remove': lambda pid, _: self.cart_service.remove_item(pid),
                'update': lambda pid, qty: self.cart_service.update_quantity(pid, qty),
                'clear': lambda _, __: self.cart_service.clear_cart()
            }
            logger.info(f"CartController initialized for cart {cart_id}")
        except CartNotFoundError:
            logger.error(f"Cart not found: {cart_id}")
            raise CartNotFoundError(cart_id)
        except CartAlreadyCheckedOutError as e:
            logger.error(f"Cart already checked out: {cart_id}")
            raise CartAlreadyCheckedOutError(str(e))

    def format_cart_response(self) -> Dict[str, Any]:
        """Format cart data for frontend consumption."""
        cart = self.cart_service.cart
        items = cart.items.all()
        logger.info(f"Formatting cart response for cart {cart.id} with {items.count()} items")
        
        formatted_items = []
        for item in items:
            formatted_item = {
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'image': item.product.image.url if item.product.image else None,
                    'stock': item.product.stock
                },
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'total_price': str(item.total_price)
            }
            formatted_items.append(formatted_item)
            logger.info(f"Added item to response: {formatted_item}")
        
        response_data = {
            'id': cart.id,
            'items': formatted_items,
            'subtotal': str(cart.subtotal),
            'tax': str(cart.tax),
            'total': str(cart.total),
            'total_items': cart.total_items
        }
        logger.info(f"Final cart response: {response_data}")
        return response_data

    def handle_error(self, exception: Exception) -> JsonResponse:
        """Standardized error response for cart-related operations."""
        error_message = str(exception)
        error_map = {
            'InvalidQuantityError': {
                'error': 'Invalid quantity specified',
                'detail': 'Please enter a valid number greater than 0.'
            },
            'InsufficientStockError': {
                'error': 'Not enough items in stock',
                'detail': 'The requested quantity exceeds available stock.'
            },
            'CartNotFoundError': {
                'error': 'Cart not found',
                'detail': 'The requested cart could not be found.'
            },
            'CartAlreadyCheckedOutError': {
                'error': 'Cart already checked out',
                'detail': 'This cart has already been processed.'
            }
        }
        
        error_info = error_map.get(exception.__class__.__name__, {
            'error': 'Unexpected error',
            'detail': error_message
        })
        
        logger.error(f"Cart operation error: {error_info['error']} - {error_info['detail']}")
        return JsonResponse(error_info, status=400)

    def modify_cart(self, action: str, product_id: Optional[int] = None, 
                   quantity: Optional[int] = None) -> JsonResponse:
        """Execute cart modifications using command pattern with lambdas."""
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
            result = command(product_id, quantity)
            logger.info(f"Command result: {result}")
            
            # Return updated cart data
            response_data = self.format_cart_response()
            logger.info(f"Modified cart response: {response_data}")
            return JsonResponse(response_data)

        except (InvalidQuantityError, InsufficientStockError, 
                CartAlreadyCheckedOutError, CartNotFoundError) as e:
            return self.handle_error(e)
        except Exception as e:
            logger.exception(f"Unexpected error during cart operation: {str(e)}")
            return JsonResponse({
                'error': 'Server error',
                'detail': 'An unexpected error occurred. Please try again later.'
            }, status=500)

    def view_cart(self) -> JsonResponse:
        """Retrieve the cart's data."""
        try:
            response_data = self.format_cart_response()
            logger.info(f"View cart response: {response_data}")
            return JsonResponse(response_data)
        except Exception as e:
            logger.exception(f"Error viewing cart: {str(e)}")
            return JsonResponse({
                'error': 'Error viewing cart',
                'detail': str(e)
            }, status=400)

    # Interface methods using the command pattern
    def add_item(self, product_id: int, quantity: int) -> JsonResponse:
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
