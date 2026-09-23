"""
Seed the database with demo categories and products so the storefront
isn't empty on first run.

Usage: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product


class Command(BaseCommand):
    help = "Seed the database with demo categories and products."

    def handle(self, *args, **options):
        categories_data = [
            ("Electronics", "Phones, laptops, gadgets and accessories."),
            ("Fashion", "Clothing, shoes and accessories for everyone."),
            ("Home & Living", "Furniture, decor and kitchen essentials."),
            ("Books", "Fiction, non-fiction and educational books."),
        ]

        categories = {}
        for name, description in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': description})
            categories[name] = cat

        products_data = [
            ("Wireless Bluetooth Headphones", "Electronics", 49.99, 39.99, 25, True, True, False),
            ("Smartphone 128GB", "Electronics", 399.00, None, 15, True, False, True),
            ("4K Ultra HD Smart TV 55\"", "Electronics", 549.00, 499.00, 8, False, True, True),
            ("Men's Classic Denim Jacket", "Fashion", 59.99, None, 30, True, False, False),
            ("Women's Running Shoes", "Fashion", 74.99, 64.99, 20, True, True, True),
            ("Leather Handbag", "Fashion", 89.00, None, 12, False, False, False),
            ("Modern Sofa Set (3-Seater)", "Home & Living", 799.00, 699.00, 5, True, False, True),
            ("Ceramic Dinnerware Set (16-Piece)", "Home & Living", 65.00, None, 18, False, True, False),
            ("Minimalist Table Lamp", "Home & Living", 34.99, None, 22, False, True, False),
            ("The Art of Clean Code", "Books", 24.99, None, 40, True, False, True),
            ("Atomic Habits", "Books", 18.99, 15.99, 50, True, True, True),
            ("A Brief History of Time", "Books", 21.50, None, 17, False, False, False),
        ]

        created_count = 0
        for name, cat_name, price, discount, stock, featured, is_new, best_seller in products_data:
            _, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': categories[cat_name],
                    'description': f"High quality {name.lower()} available now at a great price. "
                                    f"Fast shipping and easy returns.",
                    'short_description': f"Great value {name.lower()}.",
                    'price': price,
                    'discount_price': discount,
                    'stock': stock,
                    'is_featured': featured,
                    'is_new_arrival': is_new,
                    'is_best_seller': best_seller,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(categories)} categories ensured, {created_count} new products created."
        ))
