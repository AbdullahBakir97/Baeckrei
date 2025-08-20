"""Cart event logging service."""
from typing import Optional, Dict, Any
from django.utils import timezone
from .event_logger import CartEventLogger
from ..constants import CART_EVENT_TYPES
from apps.core.utils.json_encoder import ExtendedJSONEncoder
import uuid
import json

class CartEventService:
    """Service for logging cart-related events."""
    
    _event_logger = None
    
    @classmethod
    def _get_logger(cls):
        """Get or create event logger instance."""
        if cls._event_logger is None:
            # Import here to avoid circular imports
            from ..models import CartEvent
            cls._event_logger = CartEventLogger(CartEvent)
        return cls._event_logger
    
    @classmethod
    def log_event(cls, cart: 'Cart', event_type: str, product: Optional['Product'] = None,
                 quantity: Optional[int] = None, source: str = 'cart_service',
                 details: Optional[Dict[str, Any]] = None) -> 'CartEvent':
        """
        Log a cart event using the CartEventLogger.
        
        Args:
            cart: Cart instance
            event_type: Type of event (e.g., 'STOCK_UPDATE', 'QUANTITY_UPDATE')
            product: Optional product involved in the event
            quantity: Optional quantity involved in the event
            source: Source of the event, defaults to 'cart_service'
            details: Additional event details
            
        Returns:
            CartEvent instance
        """
        # Validate event type
        valid_event_types = [event_type for event_type, _ in CART_EVENT_TYPES]
        if event_type not in valid_event_types:
            raise ValueError(f"Invalid event type: {event_type}. Must be one of {valid_event_types}")

        # Ensure details is a dict and add metadata
        event_details = {
            'timestamp': timezone.now().isoformat(),
            'operation_id': str(uuid.uuid4()),
            'source': source,
            **(details or {})
        }
        
        # Convert to JSON to validate serialization
        json.dumps(event_details, cls=ExtendedJSONEncoder)
        
        # Use CartEventLogger (singleton pattern)
        return cls._get_logger().log_cart_event(
            cart=cart,
            event_type=event_type,
            product=product,
            quantity=quantity,
            details=event_details
        )
