from .models import Cart

def cart_count(request):
    """Add cart count to all templates."""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0
    else:
        cart_count = 0
    
    return {
        'cart_count': cart_count,
        'cart_items_count': cart_count
    }
