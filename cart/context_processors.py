from .models import Cart


def cart_summary(request):
    """Expose the current user's cart item count to every template (for the navbar badge)."""
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.total_items
    return {'cart_items_count': count}
