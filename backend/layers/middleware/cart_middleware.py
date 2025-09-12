"""Cart middleware for handling cart state in requests."""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.db import transaction
from apps.cart.services.cart_retriever import CartRetriever
from apps.cart.models import Cart
from apps.cart.commands.cart_commands import ValidateCartCommand, RetrieveCartCommand, ExpireCartCommand
from apps.cart.exceptions import VersionConflict
from apps.core.exceptions import VersionConflictError
import logging

logger = logging.getLogger(__name__)

class CartMiddleware(MiddlewareMixin):
    """Middleware to attach cart to request."""

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cart_cache_timeout = getattr(settings, 'CART_CACHE_TIMEOUT', 300)
        self._cart_retriever = CartRetriever()

    def _get_cache_key(self, request: HttpRequest) -> str:
        """Get cache key for request."""
        if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request, 'customer') and request.customer:
            return f"cart:user:{request.user.id}"
        
        if not request.session.session_key:
            request.session.create()
        return f"cart:session:{request.session.session_key}"

    def _cache_cart(self, request: HttpRequest, cart: Cart) -> None:
        """Cache cart using appropriate key."""
        if not cart or cart.completed or cart.is_expired():
            return
            
        cache_key = self._get_cache_key(request)
        if cache_key:
            cache.set(cache_key, cart, self.cart_cache_timeout)
            logger.debug(f"Cached cart {cart.id} with key {cache_key}")

    def _handle_expired_cart(self, request: HttpRequest, cart: Cart) -> None:
        """Handle expired cart by marking it as completed and removing from cache."""
        try:
            command = ExpireCartCommand(cart)
            command.execute()
            
            cache_key = self._get_cache_key(request)
            if cache_key:
                cache.delete(cache_key)
                logger.debug(f"Removed expired cart {cart.id} from cache with key {cache_key}")
        except Exception as e:
            logger.error(f"Error handling expired cart: {str(e)}", exc_info=True)

    def _should_process_request(self, request: HttpRequest) -> bool:
        """Check if request should be processed."""
        return not request.path.startswith(('/admin/', '/static/', '/media/'))

    def process_request(self, request: HttpRequest) -> None:
        """Process request to attach cart."""
        if not self._should_process_request(request):
            return

        try:
            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
                request.session.save()

            # Get cart from retriever
            request.cart = self._cart_retriever.get_cart(request)
            
            # Cache cart if needed
            if request.cart:
                self._cache_cart(request, request.cart)
        except (VersionConflictError, VersionConflict) as e:
            logger.warning(f"Version conflict retrieving cart: {str(e)}")
            request.cart = None
            # Clear cache to force refresh
            cache_key = self._get_cache_key(request)
            if cache_key:
                cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cart: {str(e)}")
            request.cart = None

    def process_response(self, request: HttpRequest, response):
        """Process response to update cart cache if needed."""
        if hasattr(request, 'cart') and request.cart:
            try:
                # Validate cart version before caching
                command = ValidateCartCommand(request.cart)
                cart = command.execute()
                if cart:
                    self._cache_cart(request, cart)
                else:
                    # Remove invalid cart from cache
                    cache_key = self._get_cache_key(request)
                    if cache_key:
                        cache.delete(cache_key)
            except (VersionConflictError, VersionConflict) as e:
                logger.warning(f"Version conflict in process_response: {str(e)}")
                # Remove conflicted cart from cache
                cache_key = self._get_cache_key(request)
                if cache_key:
                    cache.delete(cache_key)
                # Set cart to None to force refresh on next request
                request.cart = None
            except Exception as e:
                logger.error(f"Error in process_response: {str(e)}")
                
        return response
