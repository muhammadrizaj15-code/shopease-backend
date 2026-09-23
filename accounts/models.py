from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extends Django's built-in User model with e-commerce specific fields:
    role (customer/admin), phone, address and avatar.
    """

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Address fields
    address_line = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="Uzbekistan")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def full_address(self):
        parts = [self.address_line, self.city, self.region, self.postal_code, self.country]
        return ", ".join([p for p in parts if p])

    @property
    def is_admin_role(self):
        return self.role == 'admin' or self.user.is_staff


# Automatically create/update a Profile whenever a User is created/saved.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure a profile always exists (e.g. for superusers created via createsuperuser)
        Profile.objects.get_or_create(user=instance)
