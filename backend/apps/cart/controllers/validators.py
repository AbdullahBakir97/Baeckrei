"""Validators for cart operations."""

from typing import Dict, Any, Optional, Tuple
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpRequest
from apps.cart.exceptions import InvalidQuantityError
from .response_factory import CartResponseFactory
import uuid
import logging

logger = logging.getLogger(__name__)

class CartRequestValidator:
    """Validator for cart operation requests."""
    
    def __init__(self):
        """Initialize validator."""
        self.response_factory = CartResponseFactory()
        
    def validate_cart_operation(
        self,
        request: HttpRequest,
        required_fields: Optional[list] = None,
        operation_type: Optional[str] = None
    ) -> Tuple[bool, Optional[Response], Optional[Dict]]:
        """Validate cart operation request."""
        try:
            # Get request data
            data = self._get_request_data(request)
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return False, self.response_factory.error_response(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        error_type='missing_fields'
                    ), None
                    
            # Validate product ID if present
            if 'product_id' in data:
                try:
                    data['product_id'] = uuid.UUID(str(data['product_id']))
                except (ValueError, AttributeError, TypeError):
                    return False, self.response_factory.error_response(
                        "Invalid product ID format",
                        error_type='invalid_product'
                    ), None
                    
            # Validate quantity if present
            if 'quantity' in data:
                try:
                    quantity = int(data['quantity'])
                    if quantity < 1:
                        raise InvalidQuantityError(quantity)
                    data['quantity'] = quantity
                except (ValueError, TypeError):
                    return False, self.response_factory.error_response(
                        "Quantity must be a valid integer",
                        error_type='invalid_quantity'
                    ), None
                except InvalidQuantityError as e:
                    return False, self.response_factory.error_response(
                        str(e),
                        error_type='invalid_quantity'
                    ), None
                    
            return True, None, data
            
        except Exception as e:
            logger.error(f"Error validating cart operation: {str(e)}")
            return False, self.response_factory.error_response(
                "Invalid request format",
                error_type='validation_error'
            ), None
            
    def _get_request_data(self, request: HttpRequest) -> Dict[str, Any]:
        """Get data from request, handling both GET and POST methods."""
        if request.method == 'GET':
            return request.GET.dict()
        return request.data if hasattr(request, 'data') else request.POST.dict()
