from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Avg


class Brand(models.Model):
    """Product brand/manufacturer, e.g. Apple, Nike, Samsung."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Freeform product tag used for filtering/search."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Product category."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """A single product available for sale."""
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )

    brand = models.ForeignKey(
        Brand,
        related_name='products',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='products',
        blank=True
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="If set, shown as the sale price."
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created_at'])
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if not self.sku:
            self.sku = (
                f"SKU-{slugify(self.name)[:10].upper()}"
                f"-{Product.objects.count() + 1}"
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'products:product_detail',
            args=[self.slug]
        )

    @property
    def current_price(self):
        return (
            self.discount_price
            if self.discount_price
            else self.price
        )

    @property
    def is_on_sale(self):
        return bool(
            self.discount_price
            and self.discount_price < self.price
        )

    @property
    def discount_percent(self):
        if self.is_on_sale:
            return round(
                (1 - (self.discount_price / self.price)) * 100
            )
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(
            Avg('rating')
        )['rating__avg']

        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        return self.reviews.count()


# =========================================================
# PRODUCT VARIANT
# =========================================================

class ProductVariant(models.Model):
    """
    Product variant such as:
    Color + Storage + Image + Price + Stock
    """

    product = models.ForeignKey(
        Product,
        related_name='variants',
        on_delete=models.CASCADE
    )

    color = models.CharField(max_length=50)

    color_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Hex color, e.g. #C0C0C0"
    )

    storage = models.CharField(max_length=50)

    image = models.ImageField(
        upload_to='products/variants/',
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['color', 'storage']

        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'storage'],
                name='unique_product_color_storage'
            )
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.color} - "
            f"{self.storage}"
        )

    @property
    def current_price(self):
        if self.discount_price:
            return self.discount_price

        if self.price:
            return self.price

        return self.product.current_price

    @property
    def is_on_sale(self):
        return bool(
            self.discount_price
            and self.price
            and self.discount_price < self.price
        )

    @property
    def discount_percent(self):
        if self.is_on_sale:
            return round(
                (1 - (self.discount_price / self.price)) * 100
            )

        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        if not self.sku:
            base = slugify(
                f"{self.product.name}-{self.color}-{self.storage}"
            )[:70]

            self.sku = base.upper()

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Additional gallery images for a product."""

    product = models.ForeignKey(
        Product,
        related_name='gallery_images',
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to='products/gallery/'
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True
    )

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    """Technical specification."""

    product = models.ForeignKey(
        Product,
        related_name='specifications',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    value = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return (
            f"{self.product.name} — "
            f"{self.name}: {self.value}"
        )


class Review(models.Model):
    """Customer review / rating for a product."""

    RATING_CHOICES = [
        (i, str(i))
        for i in range(1, 6)
    ]

    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.product.name} "
            f"({self.rating}★)"
        )


class Wishlist(models.Model):
    """A user's saved-for-later products."""

    user = models.ForeignKey(
        User,
        related_name='wishlist_items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        related_name='wishlisted_by',
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return (
            f"{self.user.username} ♥ "
            f"{self.product.name}"
        )