from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from datetime import timedelta
import json

from products.models import Product, Category, Brand
from orders.models import Order, OrderItem
from cart.models import Coupon
from .decorators import staff_required
from .forms import ProductForm, CategoryForm, OrderStatusForm, BrandForm


# =========================================================
# DASHBOARD HOME - statistics, recent orders, revenue
# =========================================================
@staff_required
def dashboard_home(request):
    total_revenue = Order.objects.exclude(status='cancelled').aggregate(Sum('total'))['total__sum'] or 0
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:5]

    # Revenue for the last 7 days (for a simple chart)
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_sales_qs = (
        Order.objects.filter(created_at__gte=seven_days_ago).exclude(status='cancelled')
        .annotate(day=TruncDate('created_at'))
        .values('day').annotate(total=Sum('total')).order_by('day')
    )
    # Convert to a plain list of {day: 'YYYY-MM-DD', total: float} dicts so it can be safely
    # dumped as JSON into the template for Chart.js (Decimal/date objects aren't JSON-serializable by default).
    daily_sales_json = json.dumps([
        {'day': row['day'].strftime('%Y-%m-%d'), 'total': float(row['total'] or 0)}
        for row in daily_sales_qs
    ])

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'daily_sales': daily_sales_json,
    }
    return render(request, 'dashboard/home.html', context)


# =========================================================
# PRODUCT CRUD
# =========================================================
@staff_required
def product_list(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/product_list.html', {'page_obj': page_obj})


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect('dashboard:product_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('dashboard:product_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Edit Product'})


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': product, 'type': 'Product'})


# =========================================================
# CATEGORY CRUD
# =========================================================
@staff_required
def category_list(request):
    categories = Category.objects.order_by('name')
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Edit Category'})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': category, 'type': 'Category'})


# =========================================================
# BRAND CRUD
# =========================================================
@staff_required
def brand_list(request):
    brands = Brand.objects.order_by('name')
    return render(request, 'dashboard/brand_list.html', {'brands': brands})


@staff_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand created successfully.")
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm()
    return render(request, 'dashboard/brand_form.html', {'form': form, 'title': 'Add Brand'})


@staff_required
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated successfully.")
            return redirect('dashboard:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'dashboard/brand_form.html', {'form': form, 'title': 'Edit Brand'})


@staff_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, "Brand deleted successfully.")
        return redirect('dashboard:brand_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': brand, 'type': 'Brand'})


# =========================================================
# COUPONS (read-only list; full CRUD available via Django admin)
# =========================================================
@staff_required
def coupon_list(request):
    coupons = Coupon.objects.order_by('-id')
    return render(request, 'dashboard/coupon_list.html', {'coupons': coupons})


# =========================================================
# ORDER MANAGEMENT
# =========================================================
@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-created_at')
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/order_list.html', {
        'page_obj': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
    })


@staff_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order {order.order_number} status updated.")
            return redirect('dashboard:order_list')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'dashboard/order_update.html', {'form': form, 'order': order})


# =========================================================
# USER MANAGEMENT
# =========================================================
@staff_required
def user_list(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    paginator = Paginator(users, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/user_list.html', {'page_obj': page_obj})


# =========================================================
# REPORTS: Sales, Products, Customers
# =========================================================
@staff_required
def reports(request):
    # Sales report - revenue by day (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sales_report = (
        Order.objects.filter(created_at__gte=thirty_days_ago).exclude(status='cancelled')
        .annotate(day=TruncDate('created_at'))
        .values('day').annotate(revenue=Sum('total'), orders=Count('id')).order_by('-day')
    )

    # Product report - best selling products by quantity sold
    product_report = (
        OrderItem.objects.values('product_name')
        .annotate(total_sold=Sum('quantity'), revenue=Sum(F('price') * F('quantity')))
        .order_by('-total_sold')[:10]
    )

    # Customer report - top customers by total spend
    customer_report = (
        Order.objects.exclude(status='cancelled')
        .values('user__username', 'user__email')
        .annotate(total_spent=Sum('total'), order_count=Count('id'))
        .order_by('-total_spent')[:10]
    )

    context = {
        'sales_report': sales_report,
        'product_report': product_report,
        'customer_report': customer_report,
    }
    return render(request, 'dashboard/reports.html', context)
