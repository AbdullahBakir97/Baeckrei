def cart_context(request):
    """
    Context processor to make cart data available in all templates
    """
    if hasattr(request, 'cart'):
        cart = request.cart
        return {
            'cart': cart,
            'cart_item_count': cart.items.count() if cart else 0,
            'cart_total': cart.total if cart else 0,
        }
    return {
        'cart': None,
        'cart_item_count': 0,
        'cart_total': 0,
    }
