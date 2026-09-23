# ShopEase — E-Commerce Management System
### Internet Do'kon Boshqaruv Tizimi

A full-stack e-commerce platform built with **Django, Bootstrap 5, HTML/CSS/JS, and SQLite/MySQL**.

## Features

- Home page (hero, featured products, new arrivals, categories, best sellers, reviews, newsletter)
- Product catalog with search, category filter, price filter, sorting, pagination
- Product detail page with gallery, quantity selector, add to cart / buy now, reviews, related products
- Shopping cart (update quantity, remove item, totals)
- Checkout (shipping info, payment method, order summary, stock deduction)
- User accounts (register, login, logout, password reset, profile & address editing, password change)
- Order history and printable invoices
- Admin dashboard (statistics, recent orders, low-stock alerts, product/category CRUD, order status updates,
  user list, sales/product/customer reports)
- Django admin panel, CSRF protection, login-required views, messages framework, media uploads

## Project Structure

```
ecommerce_project/
├── manage.py
├── requirements.txt
├── ecommerce_project/      # settings, root urls, wsgi/asgi
├── accounts/                # auth, profile, address
├── products/                 # categories, products, reviews
├── cart/                     # cart & cart items
├── orders/                   # checkout, orders, invoices
├── dashboard/                 # admin dashboard (staff-only)
├── templates/                 # base.html + all app templates
├── static/css, static/js      # Bootstrap 5 + custom styling & JS
└── media/                      # uploaded product/category images
```

## Setup Instructions

1. **Create & activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   (Remove the `mysqlclient` line from requirements.txt if you're only using SQLite.)

3. **(Optional) Configure MySQL** — by default the project uses SQLite with zero config.
   To use MySQL instead, set environment variables before running:
   ```bash
   export USE_MYSQL=True
   export MYSQL_DATABASE=ecommerce_db
   export MYSQL_USER=root
   export MYSQL_PASSWORD=yourpassword
   export MYSQL_HOST=127.0.0.1
   export MYSQL_PORT=3306
   ```
   Then create the database first: `CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4;`

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create an admin (superuser) account**
   ```bash
   python manage.py createsuperuser
   ```
   Superusers automatically get a Profile and full dashboard access (`is_staff=True`).

6. **(Optional) Seed demo data** — adds sample categories & products so the store isn't empty:
   ```bash
   python manage.py seed_demo_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   - Storefront: http://127.0.0.1:8000/
   - Django admin: http://127.0.0.1:8000/admin/
   - Custom admin dashboard: http://127.0.0.1:8000/dashboard/ (staff users only)

## Notes for Production

- Set `DJANGO_DEBUG=False` and a strong `DJANGO_SECRET_KEY` environment variable.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain(s).
- Run `python manage.py collectstatic` and serve `/static/` and `/media/` via your web server (Nginx/Apache) or a
  storage backend (e.g. S3) — Django does not serve these itself when `DEBUG=False`.
- Switch `EMAIL_BACKEND` in `settings.py` from the console backend to a real SMTP backend for password-reset
  emails to actually be delivered.
- Use a production-grade WSGI/ASGI server (Gunicorn/Uvicorn) behind a reverse proxy.

## Default currency

Prices are shown with a `$` symbol in templates for simplicity — update the templates (search for `$`) if you
need a different currency symbol/formatting, e.g. UZS.
