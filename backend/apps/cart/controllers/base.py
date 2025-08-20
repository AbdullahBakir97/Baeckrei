from typing import Dict, Any, Optional, Tuple
from rest_framework.response import Response
from rest_framework import status
from abc import ABC, abstractmethod
import logging

class BaseController(ABC):
    """Base controller class implementing common functionality."""
    
    def __init__(self):
        """Initialize controller with logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_error_response(
        self,
        detail: str,
        error_type: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        additional_data: Dict[str, Any] = None
    ) -> Response:
        """Create standardized error response."""
        error_response = {
            "detail": detail,
            "error_type": error_type,
            "status": "error"
        }
        if additional_data:
            error_response.update(additional_data)
            
        return Response(error_response, status=status_code)

    def _create_success_response(
        self,
        data: Dict[str, Any],
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """Create standardized success response."""
        return Response(data, status=status_code)

    def _log_error(
        self,
        error: Exception,
        context: str,
        log_traceback: bool = True
    ) -> None:
        """Standardized error logging."""
        self.logger.error(
            f"{context}: {str(error)}",
            exc_info=log_traceback
        )

    @abstractmethod
    def validate_request(self, request) -> Tuple[bool, Optional[Response], Optional[Dict]]:
        """Validate incoming request. Must be implemented by subclasses."""
        pass
