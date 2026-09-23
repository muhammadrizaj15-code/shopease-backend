from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Brands
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_update, name='brand_update'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),

    # Coupons
    path('coupons/', views.coupon_list, name='coupon_list'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/status/', views.order_update_status, name='order_update_status'),

    # Users
    path('users/', views.user_list, name='user_list'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
