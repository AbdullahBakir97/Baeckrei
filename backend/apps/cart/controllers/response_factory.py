"""Factory for creating standardized API responses."""

from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional

class CartResponseFactory:
    """Factory for creating standardized cart operation responses."""
    
    def success_response(self, data: Dict[str, Any], status_code: int = status.HTTP_200_OK) -> Response:
        """Create a success response."""
        return Response(data, status=status_code)
        
    def error_response(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_type: str = 'validation_error',
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Create an error response."""
        response_data = {
            'status': 'error',
            'error_type': error_type,
            'detail': {
                'message': message
            }
        }
        
        if extra_data:
            response_data['detail'].update(extra_data)
            
        return Response(response_data, status=status_code)
