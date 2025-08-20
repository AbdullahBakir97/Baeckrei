"""Cart context processor."""
from decimal import Decimal
from django.http import HttpRequest
from apps.cart.commands.cart_commands import ValidateCartCommand

def cart_context_processor(request: HttpRequest) -> dict:
    """Add cart context to templates."""
    context = {
        'cart': None,
        'cart_total': Decimal('0.00'),
        'cart_items_count': 0
    }
    
    if not hasattr(request, 'cart') or not request.cart:
        return context
        
    try:
        # Validate cart
        command = ValidateCartCommand(request.cart)
        cart = command.execute()
        
        if cart and not cart.completed:
            context.update({
                'cart': cart,
                'cart_total': cart.total,
                'cart_items_count': cart.total_items
            })
    except Exception as e:
        # Log error but don't raise to avoid breaking template rendering
        from apps.cart.services.cart_retriever import logger
        logger.error(f"Error in cart context processor: {str(e)}")
        
    return context
