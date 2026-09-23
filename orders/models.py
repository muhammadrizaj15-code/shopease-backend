from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    """A placed order with shipping information, payment method and status."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit / Debit Card'),
        ('paypal', 'PayPal'),
        ('click', 'Click'),
        ('payme', 'Payme'),
    )

    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True, blank=True)

    # Shipping information
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Uzbekistan")

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=30, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # e.g. ORD-20260801-000001 style, finalized after first save for the id
            super().save(*args, **kwargs)
            self.order_number = f"ORD-{self.created_at.strftime('%Y%m%d')}-{self.id:06d}"
            kwargs['force_insert'] = False
            return super().save(update_fields=['order_number'])
        super().save(*args, **kwargs)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """A single product line inside a placed order (snapshot of price at purchase time)."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot in case product is later deleted/renamed
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of purchase
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
