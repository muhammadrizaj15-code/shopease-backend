from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product

TAX_RATE = Decimal("0.00")  # set e.g. Decimal("0.12") for 12% VAT if needed
FLAT_SHIPPING_FEE = Decimal("15000.00")
FREE_SHIPPING_THRESHOLD = Decimal("500000.00")


class Coupon(models.Model):
    """A discount coupon that can be applied at cart/checkout time."""
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                  help_text="Percent (e.g. 10 for 10%) or fixed amount off.")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(blank=True, null=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(blank=True, null=True, help_text="Leave blank for unlimited.")
    times_used = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    def is_valid(self, order_total=None):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if now < self.valid_from:
            return False
        if self.usage_limit is not None and self.times_used >= self.usage_limit:
            return False
        if order_total is not None and order_total < self.minimum_order_amount:
            return False
        return True

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percent':
            return (subtotal * self.amount / Decimal("100")).quantize(Decimal("0.01"))
        return min(self.amount, subtotal)


class Cart(models.Model):
    """One cart per logged-in user (created on demand)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    # Kept for backward compatibility with existing templates/views.
    @property
    def total_price(self):
        return self.subtotal

    @property
    def discount_amount(self):
        if self.coupon and self.coupon.is_valid(self.subtotal):
            return self.coupon.calculate_discount(self.subtotal)
        return Decimal("0.00")

    @property
    def shipping_fee(self):
        if self.subtotal == 0:
            return Decimal("0.00")
        return Decimal("0.00") if self.subtotal >= FREE_SHIPPING_THRESHOLD else FLAT_SHIPPING_FEE

    @property
    def tax_amount(self):
        taxable = self.subtotal - self.discount_amount
        return (taxable * TAX_RATE).quantize(Decimal("0.01"))

    @property
    def grand_total(self):
        return self.subtotal - self.discount_amount + self.shipping_fee + self.tax_amount


class CartItem(models.Model):
    """A single product line inside a cart."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity
