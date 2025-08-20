from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def transfer_cart_on_login(sender, request, user, **kwargs):
    """Transfer guest cart to user cart on login."""
    from apps.cart.services.cart_retriever import CartRetriever
    from apps.cart.models import Cart, CartItem
    from apps.accounts.models import Customer
    
    try:
        # Get the stored session key
        stored_key = request.session.get('_auth_user_pre_login_session_key')
        if stored_key:
            # Find guest cart by session key
            guest_cart = Cart.objects.filter(
                session_key=stored_key,
                customer__isnull=True,
                completed=False
            ).first()

            if guest_cart and guest_cart.items.exists():
                logger.info(f"Found guest cart {guest_cart.id} with items for session {stored_key}")
                # Get or create customer cart
                customer = Customer.objects.filter(user=user).first()
                if customer:
                    # Get or create customer cart
                    customer_cart = Cart.objects.filter(
                        customer=customer,
                        completed=False
                    ).first()
                    
                    if not customer_cart:
                        customer_cart = Cart.objects.create(
                            customer=customer,
                            version=1
                        )
                        logger.info(f"Created new customer cart {customer_cart.id} for user {user.email}")
                    
                    # Merge guest cart items into customer cart
                    with transaction.atomic():
                        for item in guest_cart.items.all():
                            # Check if item already exists in customer cart
                            existing_item = customer_cart.items.filter(product=item.product).first()
                            if existing_item:
                                existing_item.quantity += item.quantity
                                existing_item.save()
                                logger.info(f"Updated quantity for existing item {item.product} in cart {customer_cart.id}")
                            else:
                                # Create new item in customer cart
                                CartItem.objects.create(
                                    cart=customer_cart,
                                    product=item.product,
                                    quantity=item.quantity
                                )
                                logger.info(f"Added new item {item.product} to cart {customer_cart.id}")
                        
                        # Mark guest cart as completed
                        guest_cart.completed = True
                        guest_cart.save()
                        
                        # Clear the preserved session key
                        del request.session['_auth_user_pre_login_session_key']
                        request.session.save()
                        
                        # Increment cart version
                        customer_cart.version += 1
                        customer_cart.save()
                        
                        logger.info(f"Successfully merged guest cart {guest_cart.id} into customer cart {customer_cart.id}")
            else:
                logger.info(f"No guest cart with items found for session {stored_key}")
        else:
            logger.info("No preserved session key found")
    except Exception as e:
        logger.error(f"Error transferring cart: {str(e)}", exc_info=True)
    
    logger.info(f"Transferred cart for user {user.email}")