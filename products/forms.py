from django import forms
from .models import Review


class ProductFilterForm(forms.Form):
    """Search, category, price and sorting filters for the product list page."""
    SORT_CHOICES = (
        ('-created_at', 'Newest'),
        ('created_at', 'Oldest'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
        ('name', 'Name: A-Z'),
        ('-name', 'Name: Z-A'),
    )

    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search products...'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Min'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Max'}))
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                              'placeholder': 'Share your thoughts about this product...'}),
        }
