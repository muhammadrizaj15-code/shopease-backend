from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout(request):
    """Checkout page: shipping info, payment method, order summary, place order."""
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if cart.total_items == 0:
        messages.warning(request, "Your cart is empty. Add some products before checking out.")
        return redirect('products:product_list')

    # Re-validate the coupon (it may have expired or hit its usage limit since it was applied)
    if cart.coupon and not cart.coupon.is_valid(cart.subtotal):
        cart.coupon = None
        cart.save(update_fields=['coupon'])
        messages.warning(request, "Your coupon is no longer valid and was removed.")

    shipping_fee = cart.shipping_fee
    discount_amount = cart.discount_amount
    tax_amount = cart.tax_amount
    total = cart.grand_total

    initial = {
        'full_name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
    }
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial.update({
            'phone': profile.phone,
            'address_line': profile.address_line,
            'city': profile.city,
            'region': profile.region,
            'postal_code': profile.postal_code,
            'country': profile.country or 'Uzbekistan',
        })

    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.subtotal = cart.subtotal
                order.discount_amount = discount_amount
                order.shipping_fee = shipping_fee
                order.tax_amount = tax_amount
                order.coupon_code = cart.coupon.code if cart.coupon else ''
                order.total = total
                order.save()

                if cart.coupon:
                    cart.coupon.times_used += 1
                    cart.coupon.save(update_fields=['times_used'])

                for cart_item in cart.items.select_related('product'):
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        price=cart_item.product.current_price,
                        quantity=cart_item.quantity,
                    )
                    # Decrease stock
                    product = cart_item.product
                    if product.stock >= cart_item.quantity:
                        product.stock -= cart_item.quantity
                        product.save(update_fields=['stock'])

                cart.items.all().delete()
                cart.coupon = None
                cart.save(update_fields=['coupon'])

            messages.success(request, f"Order {order.order_number} placed successfully!")
            return redirect('orders:order_confirmation', order_number=order.order_number)
        messages.error(request, "Please correct the errors below.")
    else:
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'shipping_fee': shipping_fee,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_detail(request, order_number):
    """Order detail / invoice page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
