"""Base command interface for cart operations."""
from typing import Optional, TypeVar, Generic
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from apps.core.exceptions import VersionConflictError
from ..strategies.base import BaseCartStrategy
from apps.cart.models import Cart, CartItem
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseCommand(Generic[T]):
    """Base command interface for cart operations."""
    
    def __init__(self, cart: Cart, strategy: BaseCartStrategy):
        """Initialize command with cart and strategy."""
        self.cart = cart
        self.strategy = strategy
        
    def execute(self) -> T:
        """Execute the command using the strategy."""
        try:
            return self._execute()
        except (VersionConflictError, DatabaseError) as e:
            # Re-raise VersionConflictError directly
            if isinstance(e, VersionConflictError):
                raise
            # Convert DatabaseError to VersionConflictError
            raise VersionConflictError(obj_type="Cart", obj_id=self.cart.pk if self.cart else None)
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise
            
    def _execute(self) -> T:
        """Internal execution method to be implemented by subclasses."""
        raise NotImplementedError
        
    def _handle_error(self, error_message: str):
        """Handle command execution errors."""
        raise ValidationError(error_message)