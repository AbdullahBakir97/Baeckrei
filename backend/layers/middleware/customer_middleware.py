"""Middleware for handling customer state in requests."""
import uuid
from typing import Optional
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from apps.accounts.models import Customer
import logging
from django.contrib.auth import get_user
from django.core.cache import cache

logger = logging.getLogger(__name__)

class CustomerMiddleware(MiddlewareMixin):
    """Middleware to attach customer to request."""
    
    def process_request(self, request: HttpRequest) -> None:
        """Process request to attach customer."""
        # Skip for admin URLs and static files
        if request.path.startswith(('/admin/', '/static/', '/media/')):
            return None

        try:
            # Log user info for debugging
            logger.debug(f"User: {request.user}")
            logger.debug(f"User type: {type(request.user)}")
            logger.debug(f"Is authenticated: {request.user.is_authenticated}")
            logger.debug(f"User ID: {request.user.id if request.user.is_authenticated else None}")

            # For authenticated users
            if request.user.is_authenticated:
                # Get or create customer
                customer = Customer.objects.filter(user=request.user).first()
                if customer:
                    request.customer = customer
                    logger.debug(f"Found customer for user {request.user.id}: {customer}")
                else:
                    # Create customer if this is a new registration
                    customer = Customer.objects.create(
                        user=request.user,
                        email=request.user.email
                    )
                    request.customer = customer
                    logger.debug(f"Created new customer for user {request.user.id}: {customer}")

                    # Preserve session key for cart merging if not already set
                    if not request.session.get('_auth_user_pre_login_session_key') and request.session.session_key:
                        request.session['_auth_user_pre_login_session_key'] = request.session.session_key
                        request.session.save()
                        logger.debug(f"Preserved session key {request.session.session_key} for new customer")
            else:
                logger.debug("Anonymous user, no customer set")
                request.customer = None

        except Exception as e:
            logger.error(f"Error in CustomerMiddleware: {str(e)}", exc_info=True)
            request.customer = None

        return None

    def process_response(self, request: HttpRequest, response):
        """Process response."""
        return response
