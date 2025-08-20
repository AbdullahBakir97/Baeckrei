"""Cart-specific event logging service."""
from typing import Any, Dict, Optional
from django.core.exceptions import ValidationError
import logging
from apps.core.services.event_logger import BaseEventLogger
from ..models import CartEvent

logger = logging.getLogger(__name__)

class CartEventLogger(BaseEventLogger):
    """Cart-specific event logger implementation."""
    
    def log_cart_event(self, cart: 'Cart', event_type: str, product: Optional['Product'] = None,
                      quantity: Optional[int] = None, details: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> CartEvent:
        """
        Log a cart-specific event.
        
        Args:
            cart: Cart instance
            event_type: Type of event
            product: Optional product involved
            quantity: Optional quantity involved
            details: Optional event details
            metadata: Optional event metadata
            
        Returns:
            Created cart event
        """
        return self.log(
            event_type=event_type,
            related_object=cart,
            details={
                'product_id': product.id if product else None,
                'quantity': quantity,
                **(details or {})
            },
            metadata=metadata
        )
