from django.db import connection
import logging

logger = logging.getLogger(__name__)

def cart_context(request):
    """Add cart information to the template context.
    
    Returns minimal cart data for template rendering.
    Checks for table/column existence to handle migrations gracefully.
    """
    default_response = {'cart_total': 0, 'cart_items_count': 0}
    
    try:
        # Check if the cart_cartitem table exists and has the unit_price column
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sqlite_master 
                WHERE type='table' AND name='cart_cartitem'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                logger.debug("Cart table does not exist yet")
                return default_response

            cursor.execute("""
                SELECT COUNT(*) 
                FROM pragma_table_info('cart_cartitem') 
                WHERE name='unit_price'
            """)
            column_exists = cursor.fetchone()[0] > 0

            if not column_exists:
                logger.debug("Unit price column does not exist yet")
                return default_response

        if hasattr(request, 'cart') and request.cart:
            cart = request.cart
            context = {
                'cart_total': str(cart.total),  # Convert Decimal to string for JSON
                'cart_items_count': cart.total_items
            }
            logger.debug(f"Cart context for cart {cart.id}: {context}")
            return context
            
    except Exception as e:
        logger.error(f"Error in cart context processor: {str(e)}")
    
    return default_response
