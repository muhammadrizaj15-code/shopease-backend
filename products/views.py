from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse

from .models import (
    Category,
    Product,
    ProductVariant,
    Review,
    Brand,
    Wishlist,
)

from .forms import ProductFilterForm, ReviewForm


RECENTLY_VIEWED_SESSION_KEY = 'recently_viewed_ids'
RECENTLY_VIEWED_MAX = 8


def home(request):

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-created_at')[:8]

    new_arrivals = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:8]

    best_sellers = Product.objects.filter(
        is_active=True,
        is_best_seller=True
    ).order_by('-created_at')[:8]

    categories = Category.objects.filter(
        is_active=True
    ).order_by('-created_at')[:8]

    latest_reviews = Review.objects.select_related(
        'user',
        'product'
    ).order_by('-created_at')[:6]

    flash_sale_products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False
    ).order_by('-created_at')[:8]

    brands = Brand.objects.filter(
        is_active=True
    )[:10]

    viewed_ids = request.session.get(
        RECENTLY_VIEWED_SESSION_KEY,
        []
    )

    recently_viewed = (
        Product.objects.filter(
            id__in=viewed_ids,
            is_active=True
        )[:6]
        if viewed_ids
        else []
    )

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
        'latest_reviews': latest_reviews,
        'flash_sale_products': flash_sale_products,
        'brands': brands,
        'recently_viewed': recently_viewed,
    }

    return render(
        request,
        'products/home.html',
        context
    )


def product_list(request, category_slug=None):

    products = Product.objects.filter(
        is_active=True
    ).select_related('category')

    category = None

    if category_slug:

        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_active=True
        )

        products = products.filter(
            category=category
        )

    form = ProductFilterForm(request.GET or None)

    if form.is_valid():

        q = form.cleaned_data.get('q')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort = form.cleaned_data.get('sort')

        if q:
            products = products.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(short_description__icontains=q)
            )

        if min_price is not None:
            products = products.filter(
                price__gte=min_price
            )

        if max_price is not None:
            products = products.filter(
                price__lte=max_price
            )

        if sort:
            products = products.order_by(sort)

    brand_slugs = request.GET.getlist('brand')

    if brand_slugs:

        products = products.filter(
            brand__slug__in=brand_slugs
        )

    if request.GET.get('availability') == 'in_stock':

        products = products.filter(
            stock__gt=0
        )

    min_rating = request.GET.get('rating')

    if min_rating:

        try:

            min_rating = int(min_rating)

            product_ids = [
                p.id
                for p in products
                if p.average_rating >= min_rating
            ]

            products = products.filter(
                id__in=product_ids
            )

        except ValueError:
            pass

    paginator = Paginator(
        products,
        getattr(settings, 'PRODUCTS_PER_PAGE', 12)
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    categories = Category.objects.filter(
        is_active=True
    )

    brands = Brand.objects.filter(
        is_active=True
    )

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'form': form,
        'categories': categories,
        'brands': brands,
        'selected_brands': brand_slugs,
        'current_category': category,
    }

    return render(
        request,
        'products/product_list.html',
        context
    )


def product_detail(request, slug):

    # =====================================================
    # PRODUCT
    # =====================================================

    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    # =====================================================
    # VARIANTS
    # =====================================================

    variants = ProductVariant.objects.filter(
        product=product,
        is_active=True
    ).order_by(
        'color',
        'storage'
    )

    # =====================================================
    # COLORS
    # =====================================================

    colors = variants.values(
        'color',
        'color_code'
    ).distinct()

    # =====================================================
    # STORAGES
    # =====================================================

    storages = variants.values_list(
        'storage',
        flat=True
    ).distinct()

    # =====================================================
    # VARIANTS JSON DATA
    # =====================================================

    variants_data = []

    for variant in variants:

        variants_data.append({

            'id': variant.id,

            'color': variant.color or '',

            'color_code': variant.color_code or '',

            'storage': variant.storage or '',

            'price': (
                str(variant.price)
                if variant.price is not None
                else ''
            ),

            'discount_price': (
                str(variant.discount_price)
                if variant.discount_price is not None
                else ''
            ),

            'stock': int(
                variant.stock or 0
            ),

            'sku': variant.sku or '',

            'image': (
                variant.image.url
                if variant.image
                else ''
            ),
        })

    # =====================================================
    # RELATED PRODUCTS
    # =====================================================

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(
        pk=product.pk
    )[:4]

    # =====================================================
    # REVIEWS
    # =====================================================

    reviews = product.reviews.select_related(
        'user'
    ).all()

    review_form = ReviewForm()

    user_has_reviewed = False

    in_wishlist = False

    if request.user.is_authenticated:

        user_has_reviewed = reviews.filter(
            user=request.user
        ).exists()

        in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # =====================================================
    # REVIEW SUBMIT
    # =====================================================

    if request.method == 'POST':

        if not request.user.is_authenticated:

            messages.warning(
                request,
                "Please log in to leave a review."
            )

            return redirect(
                'accounts:login'
            )

        if user_has_reviewed:

            messages.warning(
                request,
                "You have already reviewed this product."
            )

            return redirect(
                'products:product_detail',
                slug=slug
            )

        review_form = ReviewForm(
            request.POST
        )

        if review_form.is_valid():

            review = review_form.save(
                commit=False
            )

            review.product = product

            review.user = request.user

            review.save()

            messages.success(
                request,
                "Thank you for your review!"
            )

            return redirect(
                'products:product_detail',
                slug=slug
            )

    # =====================================================
    # RECENTLY VIEWED
    # =====================================================

    viewed_ids = request.session.get(
        RECENTLY_VIEWED_SESSION_KEY,
        []
    )

    recently_viewed = Product.objects.filter(
        id__in=[
            i for i in viewed_ids
            if i != product.id
        ],
        is_active=True
    )[:RECENTLY_VIEWED_MAX]

    viewed_ids = [
        product.id
    ] + [
        i for i in viewed_ids
        if i != product.id
    ]

    request.session[
        RECENTLY_VIEWED_SESSION_KEY
    ] = viewed_ids[:RECENTLY_VIEWED_MAX]

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'product': product,

        'variants': variants,

        'variants_data': variants_data,

        'colors': colors,

        'storages': storages,

        'related_products': related_products,

        'reviews': reviews,

        'review_form': review_form,

        'user_has_reviewed': user_has_reviewed,

        'in_wishlist': in_wishlist,

        'specifications': product.specifications.all(),

        'recently_viewed': recently_viewed,
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )


def category_list(request):

    categories = Category.objects.filter(
        is_active=True
    )

    return render(
        request,
        'products/category_list.html',
        {
            'categories': categories
        }
    )


@login_required
def wishlist_view(request):

    items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        'product'
    )

    return render(
        request,
        'products/wishlist.html',
        {
            'items': items
        }
    )


@login_required
def wishlist_toggle(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:

        item.delete()

        messages.info(
            request,
            f'"{product.name}" removed from your wishlist.'
        )

    else:

        messages.success(
            request,
            f'"{product.name}" added to your wishlist.'
        )

    return redirect(
        request.POST.get('next')
        or product.get_absolute_url()
    )


def live_search(request):

    q = request.GET.get(
        'q',
        ''
    ).strip()

    results = []

    if len(q) >= 2:

        matches = Product.objects.filter(
            Q(name__icontains=q) |
            Q(category__name__icontains=q),
            is_active=True
        ).select_related(
            'category'
        )[:6]

        for p in matches:

            results.append({

                'name': p.name,

                'url': p.get_absolute_url(),

                'price': str(
                    p.current_price
                ),

                'image': (
                    p.image.url
                    if p.image
                    else ''
                ),

                'category': p.category.name,
            })

    return JsonResponse({
        'results': results
    })