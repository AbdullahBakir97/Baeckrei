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

        if hasattr(request, 'cart') and request.cart:
            cart = request.cart
            items = cart.items.values('product__name', 'quantity', 'product__price', 'product__image')
            return {
                'cart_total': cart.total if cart else 0,
                'cart_items_count': cart.total_items if cart else 0,
                'cart_items': list(items),  # Pass detailed items to the context
            }
    except Exception as e:
        # Handle any exceptions (e.g., during migrations)
        print(f"Error in cart_context: {e}")
    
    # Default context
    return {'cart_total': 0, 'cart_items_count': 0, 'cart_items': []}
