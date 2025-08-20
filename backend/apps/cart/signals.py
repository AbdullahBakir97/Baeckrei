"""Cart lifecycle signal handlers."""
from typing import Any, Dict, Optional
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from django.http import HttpRequest
from django.utils import timezone
from .commands.cart_commands import (
    CreateCartCommand,
    GetSessionCartCommand,
    GetCustomerCartCommand,
    ExpireCartCommand
)
from .models import Cart
from .services.cart_event_service import CartEventService
import logging

logger = logging.getLogger(__name__)

# Custom signals for cart lifecycle events
visitor_cart_created = Signal()  # Sent when a visitor's first cart is created
customer_cart_created = Signal()  # Sent when a customer's first cart is created
cart_expired = Signal()  # Sent when cart expires due to session end or timeout

class CartLifecycleManager:
    """Manager for handling cart lifecycle signals."""
    
    def __init__(self):
        self._event_service = CartEventService()
        
    @staticmethod
    @receiver(user_logged_in)
    def handle_user_login(sender: Any, request: HttpRequest, user: Any, **kwargs: Any) -> None:
        """Handle user login by merging session cart into customer cart."""
        try:
            # Get session cart if exists
            session_key = request.session.session_key
            if session_key:
                session_cart_command = GetSessionCartCommand(session_key)
                session_cart = session_cart_command.execute()
                
                if session_cart:
                    # Get or create customer cart
                    customer_cart_command = GetCustomerCartCommand(user.customer)
                    customer_cart = customer_cart_command.execute()
                    
                    if not customer_cart:
                        create_command = CreateCartCommand(customer=user.customer)
                        customer_cart = create_command.execute()
                        customer_cart_created.send(
                            sender=CartLifecycleManager,
                            cart=customer_cart,
                            customer=user.customer
                        )
                    
        except Exception as e:
            logger.error(f"Error handling user login: {str(e)}")
    
    @staticmethod
    @receiver(user_logged_out)
    def handle_user_logout(sender: Any, request: HttpRequest, user: Any, **kwargs: Any) -> None:
        """Handle user logout by creating a new session cart."""
        try:
            # Create new session cart for continued shopping
            if request.session.session_key:
                create_command = CreateCartCommand(session_key=request.session.session_key)
                cart = create_command.execute()
                
                visitor_cart_created.send(
                    sender=CartLifecycleManager,
                    cart=cart,
                    session_key=request.session.session_key
                )
                
        except Exception as e:
            logger.error(f"Error handling user logout: {str(e)}")
    
    @staticmethod
    @receiver(post_save, sender=Session)
    def handle_session_start(sender: Session, instance: Session, created: bool, **kwargs: Any) -> None:
        """Handle new session by creating a cart for the visitor."""
        if created:
            try:
                # Create new session cart
                create_command = CreateCartCommand(session_key=instance.session_key)
                cart = create_command.execute()
                
                visitor_cart_created.send(
                    sender=CartLifecycleManager,
                    cart=cart,
                    session_key=instance.session_key
                )
                
            except Exception as e:
                logger.error(f"Error creating visitor cart: {str(e)}")
    
    @staticmethod
    @receiver(post_delete, sender=Session)
    def handle_session_end(sender: Session, instance: Session, **kwargs: Any) -> None:
        """Handle session end by expiring associated cart."""
        try:
            # Find and expire session cart
            session_cart_command = GetSessionCartCommand(instance.session_key)
            cart = session_cart_command.execute()
            
            if cart and not cart.completed:
                expire_command = ExpireCartCommand(cart)
                if expire_command.execute():
                    cart_expired.send(
                        sender=CartLifecycleManager,
                        cart=cart,
                        reason='session_ended',
                        expired_at=timezone.now()
                    )
                    
        except Exception as e:
            logger.error(f"Error handling session end: {str(e)}")
    
    def check_cart_expiry(self, cart: Cart, expiry_hours: int = 24) -> None:
        """Check and handle cart expiration."""
        if cart and not cart.completed:
            last_modified = cart.updated_at or cart.created_at
            expiry_time = last_modified + timezone.timedelta(hours=expiry_hours)
            
            if timezone.now() > expiry_time:
                expire_command = ExpireCartCommand(cart)
                if expire_command.execute():
                    cart_expired.send(
                        sender=self.__class__,
                        cart=cart,
                        reason='time_expired',
                        expired_at=timezone.now()
                    )
