from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem, Coupon


def _get_or_create_cart(request):
    cart, _created = Cart.objects.get_or_create(user=request.user)
    return cart


@login_required
def cart_detail(request):
    """Shopping cart page: shows all items, quantities and total price."""
    cart = _get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@login_required
@require_POST
def cart_add(request, product_id):
    """Add a product to the cart (or increase quantity if already present)."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_or_create_cart(request)

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    item, created = CartItem.objects.get_or_create(cart=cart, product=product,
                                                     defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    messages.success(request, f'"{product.name}" was added to your cart.')

    if request.POST.get('buy_now'):
        return redirect('orders:checkout')
    return redirect(request.POST.get('next') or 'cart:cart_detail')


@login_required
@require_POST
def cart_update(request, item_id):
    """Update the quantity of a specific cart item."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        item.delete()
        messages.info(request, "Item removed from cart.")
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, "Cart updated.")
    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_remove(request, item_id):
    """Remove an item from the cart entirely."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart:cart_detail')


@login_required
@require_POST
def apply_coupon(request):
    """Apply a discount coupon code to the cart."""
    cart = _get_or_create_cart(request)
    code = request.POST.get('code', '').strip().upper()

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect('cart:cart_detail')

    if not coupon.is_valid(cart.subtotal):
        messages.error(request, "This coupon is expired, inactive, or your order doesn't meet its minimum amount.")
        return redirect('cart:cart_detail')

    cart.coupon = coupon
    cart.save(update_fields=['coupon'])
    messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
    return redirect('cart:cart_detail')


@login_required
@require_POST
def remove_coupon(request):
    cart = _get_or_create_cart(request)
    cart.coupon = None
    cart.save(update_fields=['coupon'])
    messages.info(request, "Coupon removed.")
    return redirect('cart:cart_detail')
