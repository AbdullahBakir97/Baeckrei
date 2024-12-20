from django.utils.deprecation import MiddlewareMixin
from .models import Cart

class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get or create cart for the customer
        if hasattr(request, 'customer'):
            cart, created = Cart.objects.get_or_create(
                customer=request.customer,
                completed=False
            )
            request.cart = cart
        else:
            request.cart = None
