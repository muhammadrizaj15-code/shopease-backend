import os
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import openpyxl

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify

from .models import (
    Product,
    Category,
    Brand,
    ProductVariant,
)


# =========================================================
# RASMNI INTERNETDAN YUKLASH
# =========================================================

def download_image(image_url, name):
    """
    URL orqali rasmni yuklab oladi.
    Django ImageField uchun ContentFile qaytaradi.
    """

    if not image_url:
        return None, None

    image_url = str(image_url).strip()

    if not image_url.startswith(("http://", "https://")):
        return None, None

    try:

        request = Request(
            image_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/151.0 Safari/537.36"
                )
            },
        )

        with urlopen(request, timeout=20) as response:
            image_data = response.read()

        path = urlparse(image_url).path
        filename = os.path.basename(path)

        if not filename or "." not in filename:
            filename = f"{slugify(name)}.jpg"

        filename = filename[:150]

        return filename, ContentFile(image_data)

    except Exception as e:

        print("=" * 60)
        print("RASM YUKLASHDA XATO")
        print("URL:", image_url)
        print("XATO:", e)
        print("=" * 60)

        return None, None


# =========================================================
# EXCEL IMPORT
# =========================================================

def import_products_from_excel(file_path):

    workbook = openpyxl.load_workbook(
        file_path,
        data_only=True
    )

    sheet = workbook.active

    created_count = 0
    updated_count = 0

    variant_created_count = 0
    variant_updated_count = 0

    image_count = 0
    image_error_count = 0

    # =====================================================
    # EXCEL USTUNLARI
    # =====================================================
    #
    # A  name
    # B  category
    # C  brand
    # D  price
    # E  discount_price
    # F  description
    # G  stock
    # H  sku
    # I  image_url
    #
    # J  color
    # K  color_code
    # L  storage
    # M  variant_price
    # N  variant_discount_price
    # O  variant_stock
    # P  variant_sku
    # Q  variant_image_url
    # R  variant_active
    #
    # =====================================================

    with transaction.atomic():

        for row_number, row in enumerate(
            sheet.iter_rows(
                min_row=2,
                values_only=True
            ),
            start=2
        ):

            # -------------------------------------------------
            # Yetarli ustun bo'lmasa ham xato bermasin
            # -------------------------------------------------

            values = list(row)

            while len(values) < 18:
                values.append(None)

            # -------------------------------------------------
            # PRODUCT MA'LUMOTLARI
            # -------------------------------------------------

            name = values[0]
            category_name = values[1]
            brand_name = values[2]
            price = values[3]
            discount_price = values[4]
            description = values[5]
            stock = values[6]
            sku = values[7]
            image_url = values[8]

            # -------------------------------------------------
            # VARIANT MA'LUMOTLARI
            # -------------------------------------------------

            color = values[9]
            color_code = values[10]
            storage = values[11]
            variant_price = values[12]
            variant_discount_price = values[13]
            variant_stock = values[14]
            variant_sku = values[15]
            variant_image_url = values[16]
            variant_active = values[17]

            # =================================================
            # NOM BO'LMASA QATORNI TASHLAB KETAMIZ
            # =================================================

            if not name:
                continue

            name = str(name).strip()

            # =================================================
            # CATEGORY
            # =================================================

            category_name = str(
                category_name or "Other"
            ).strip()

            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "is_active": True,
                }
            )

            # =================================================
            # BRAND
            # =================================================

            brand = None

            if brand_name:

                brand_name = str(
                    brand_name
                ).strip()

                brand, _ = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={
                        "is_active": True,
                    }
                )

            # =================================================
            # PRODUCT SKU
            # =================================================

            if sku:
                sku = str(sku).strip()
            else:
                sku = ""

            # =================================================
            # PRODUCTNI TOPISH
            # =================================================

            product = None

            if sku:

                product = Product.objects.filter(
                    sku=sku
                ).first()

            # SKU bo'lmasa nom + category orqali qidiramiz

            if not product:

                product = Product.objects.filter(
                    name=name,
                    category=category
                ).first()

            # =================================================
            # PRICE
            # =================================================

            try:
                product_price = (
                    float(price)
                    if price is not None
                    else 0
                )
            except (ValueError, TypeError):
                product_price = 0

            try:
                product_discount_price = (
                    float(discount_price)
                    if discount_price is not None
                    and str(discount_price).strip() != ""
                    else None
                )
            except (ValueError, TypeError):
                product_discount_price = None

            try:
                product_stock = (
                    int(stock)
                    if stock is not None
                    else 0
                )
            except (ValueError, TypeError):
                product_stock = 0

            # =================================================
            # PRODUCT YARATISH / UPDATE
            # =================================================

            if product:

                product.name = name
                product.category = category
                product.brand = brand

                product.price = product_price
                product.discount_price = (
                    product_discount_price
                )

                product.description = str(
                    description or ""
                )

                product.stock = product_stock

                if sku:
                    product.sku = sku

                product.save()

                updated_count += 1

            else:

                product = Product.objects.create(

                    name=name,

                    category=category,

                    brand=brand,

                    price=product_price,

                    discount_price=(
                        product_discount_price
                    ),

                    description=str(
                        description or ""
                    ),

                    stock=product_stock,

                    sku=sku,
                )

                created_count += 1

            # =================================================
            # PRODUCT ASOSIY RASMI
            # =================================================

            if image_url:

                filename, image_file = download_image(
                    image_url,
                    name
                )

                if filename and image_file:

                    try:

                        product.image.save(
                            filename,
                            image_file,
                            save=True
                        )

                        image_count += 1

                    except Exception as e:

                        print(
                            f"Product rasmi saqlanmadi: "
                            f"{name} - {e}"
                        )

                        image_error_count += 1

                else:

                    image_error_count += 1

            # =================================================
            # VARIANT BOR-YO'QLIGINI TEKSHIRAMIZ
            # =================================================

            has_variant = any([
                color,
                storage,
                variant_sku,
                variant_image_url,
            ])

            if not has_variant:
                continue

            # =================================================
            # VARIANT MA'LUMOTLARINI TOZALASH
            # =================================================

            color = str(
                color or ""
            ).strip()

            color_code = str(
                color_code or ""
            ).strip()

            storage = str(
                storage or ""
            ).strip()

            if variant_sku:

                variant_sku = str(
                    variant_sku
                ).strip()

            else:

                variant_sku = ""

            # =================================================
            # VARIANT PRICE
            # =================================================

            try:

                if (
                    variant_price is not None
                    and str(variant_price).strip() != ""
                ):

                    v_price = float(
                        variant_price
                    )

                else:

                    v_price = product_price

            except (ValueError, TypeError):

                v_price = product_price

            # =================================================
            # VARIANT DISCOUNT PRICE
            # =================================================

            try:

                if (
                    variant_discount_price is not None
                    and str(
                        variant_discount_price
                    ).strip() != ""
                ):

                    v_discount_price = float(
                        variant_discount_price
                    )

                else:

                    v_discount_price = (
                        product_discount_price
                    )

            except (ValueError, TypeError):

                v_discount_price = (
                    product_discount_price
                )

            # =================================================
            # VARIANT STOCK
            # =================================================

            try:

                if (
                    variant_stock is not None
                    and str(variant_stock).strip() != ""
                ):

                    v_stock = int(
                        variant_stock
                    )

                else:

                    v_stock = product_stock

            except (ValueError, TypeError):

                v_stock = product_stock

            # =================================================
            # IS ACTIVE
            # =================================================

            if variant_active is None:

                v_active = True

            else:

                active_text = str(
                    variant_active
                ).strip().lower()

                v_active = active_text not in [
                    "no",
                    "false",
                    "0",
                    "inactive",
                ]

            # =================================================
            # VARIANTNI TOPISH
            # =================================================

            variant = None

            # Eng yaxshi usul — variant SKU orqali

            if variant_sku:

                variant = ProductVariant.objects.filter(
                    sku=variant_sku
                ).first()

            # SKU bo'lmasa product + color + storage

            if not variant:

                variant = ProductVariant.objects.filter(
                    product=product,
                    color=color,
                    storage=storage
                ).first()

            # =================================================
            # VARIANT YARATISH
            # =================================================

            if variant:

                variant.color = color
                variant.color_code = color_code
                variant.storage = storage

                variant.price = v_price
                variant.discount_price = (
                    v_discount_price
                )

                variant.stock = v_stock
                variant.sku = variant_sku
                variant.is_active = v_active

                variant.save()

                variant_updated_count += 1

            else:

                variant = ProductVariant.objects.create(

                    product=product,

                    color=color,

                    color_code=color_code,

                    storage=storage,

                    price=v_price,

                    discount_price=(
                        v_discount_price
                    ),

                    stock=v_stock,

                    sku=variant_sku,

                    is_active=v_active,
                )

                variant_created_count += 1

            # =================================================
            # VARIANT RASMI
            # =================================================

            if variant_image_url:

                filename, image_file = download_image(
                    variant_image_url,
                    f"{name}-{color}-{storage}"
                )

                if filename and image_file:

                    try:

                        variant.image.save(
                            filename,
                            image_file,
                            save=True
                        )

                        image_count += 1

                    except Exception as e:

                        print(
                            f"Variant rasmi saqlanmadi: "
                            f"{name} / {color} / {storage}"
                        )

                        print(e)

                        image_error_count += 1

                else:

                    image_error_count += 1

    # =====================================================
    # NATIJA
    # =====================================================

    return (
        created_count,
        updated_count,
        image_count,
        image_error_count,
    )