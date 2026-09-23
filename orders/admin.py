from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_method', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'full_name', 'phone', 'email')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'subtotal', 'shipping_fee', 'total')
