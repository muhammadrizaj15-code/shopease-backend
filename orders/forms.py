from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Shipping information + payment method collected at checkout."""

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'email', 'address_line', 'city', 'region',
                  'postal_code', 'country', 'payment_method', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 90 123 45 67'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Region'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                            'placeholder': 'Delivery instructions (optional)'}),
        }
