"""Cart services package."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .services import CartService
    from .cart_retriever import CartRetriever
    from .cart_event_service import CartEventService

__all__ = ['CartService', 'CartRetriever', 'CartEventService']

def get_cart_service():
    """Get cart service lazily."""
    from .services import CartService
    return CartService

def get_cart_retriever():
    """Get cart retriever lazily."""
    from .cart_retriever import CartRetriever
    return CartRetriever

def get_cart_event_service():
    """Get cart event service lazily."""
    from .cart_event_service import CartEventService
    return CartEventService