from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage

from .models import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    Review,
    Brand,
    Tag,
    Wishlist,
    ProductVariant,
)

from .import_products import import_products_from_excel


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'is_active',
        'product_count',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'brand',
        'price',
        'discount_price',
        'stock',
        'is_active',
        'is_featured',
        'is_new_arrival',
        'is_best_seller',
        'created_at',
    )

    list_filter = (
        'category',
        'brand',
        'is_active',
        'is_featured',
        'is_new_arrival',
        'is_best_seller',
    )

    search_fields = (
        'name',
        'sku',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
    ]

    list_editable = (
        'price',
        'stock',
        'is_active',
    )

    filter_horizontal = ('tags',)

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(
                    self.import_excel
                ),
                name='products_product_import_excel',
            ),
        ]

        return custom_urls + urls

    def import_excel(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')

            if not excel_file:
                messages.error(
                    request,
                    'Excel fayl tanlanmagan!'
                )

                return redirect(
                    'admin:products_product_import_excel'
                )

            if not excel_file.name.endswith(
                ('.xlsx', '.xlsm')
            ):
                messages.error(
                    request,
                    'Faqat .xlsx yoki .xlsm Excel fayl yuklang!'
                )

                return redirect(
                    'admin:products_product_import_excel'
                )

            file_path = default_storage.save(
                f'temp/{excel_file.name}',
                excel_file,
            )

            try:
                created, updated, images, image_errors = (
                    import_products_from_excel(
                        default_storage.path(file_path)
                    )
                )

                messages.success(
                    request,
                    f'Import tugadi! '
                    f'Yangi: {created} ta, '
                    f'Yangilangan: {updated} ta, '
                    f'Rasmlar: {images} ta, '
                    f'Rasm xatosi: {image_errors} ta.'
                )

            except Exception as e:
                messages.error(
                    request,
                    f'Xatolik: {e}'
                )

            finally:
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)

            return redirect(
                'admin:products_product_changelist'
            )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Import Products from Excel',
        }

        return render(
            request,
            'admin/products/product/import_excel.html',
            context,
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating',
        'created_at',
    )

    list_filter = ('rating',)

    search_fields = (
        'product__name',
        'user__username',
        'comment',
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'added_at',
    )

    search_fields = (
        'user__username',
        'product__name',
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'color',
        'storage',
        'price',
        'discount_price',
        'stock',
        'is_active',
    )

    list_filter = (
        'color',
        'storage',
        'is_active',
    )

    search_fields = (
        'product__name',
        'color',
        'storage',
        'sku',
    )