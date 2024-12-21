from django.db import connection

def cart_context(request):
    """Add cart information to the template context."""
    try:
        # Check if the cart_cartitem table exists and has the unit_price column
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sqlite_master 
                WHERE type='table' AND name='cart_cartitem'
            """)
            table_exists = cursor.fetchone()[0] > 0

            if table_exists:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pragma_table_info('cart_cartitem') 
                    WHERE name='unit_price'
                """)
                column_exists = cursor.fetchone()[0] > 0

                if not column_exists:
                    return {'cart_total': 0, 'cart_items_count': 0}

        if hasattr(request, 'cart'):
            cart = request.cart
            return {
                'cart_total': cart.total if cart else 0,
                'cart_items_count': cart.total_items if cart else 0,
            }
    except Exception:
        # During migrations or if there are any DB issues, return empty context
        pass
    
    return {'cart_total': 0, 'cart_items_count': 0}
