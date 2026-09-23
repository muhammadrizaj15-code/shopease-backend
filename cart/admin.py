from django.contrib import admin
from .models import Cart, CartItem, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'amount', 'is_active', 'valid_from', 'valid_to', 'times_used')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'updated_at')
    inlines = [CartItemInline]
