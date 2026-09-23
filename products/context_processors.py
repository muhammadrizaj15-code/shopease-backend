from .models import Category


def categories_menu(request):
    """Expose active categories to every template (used in the navbar)."""
    return {'nav_categories': Category.objects.filter(is_active=True)[:10]}


def wishlist_ids(request):
    """Expose the current user's wishlisted product IDs so product cards can show a filled heart."""
    if request.user.is_authenticated:
        from .models import Wishlist
        ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        return {'wishlist_ids': ids}
    return {'wishlist_ids': set()}
