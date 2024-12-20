import uuid
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import Customer

class CustomerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get or create customer ID from session
        customer_id = request.session.get('customer_id')
        
        if not customer_id:
            # Generate a new customer ID for anonymous users
            customer_id = str(uuid.uuid4())
            request.session['customer_id'] = customer_id
            
        # Try to get an existing customer
        if request.user.is_authenticated:
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={'customer_id': customer_id}
            )
        else:
            customer, created = Customer.objects.get_or_create(
                customer_id=customer_id,
                user=None
            )
            
        # Attach the customer to the request
        request.customer = customer
