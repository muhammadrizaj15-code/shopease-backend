"""
Django settings for ecommerce_project.
E-Commerce Management System (Internet Do'kon Boshqaruv Tizimi)
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# SECURITY
# =========================================================
# NOTE: keep the secret key secret in production and load it from an
# environment variable instead of hard-coding it.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-CHANGE-THIS-KEY-IN-PRODUCTION-0123456789'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost,shakable-backlit-evaluate.ngrok-free.dev'
).split(',')

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'https://shakable-backlit-evaluate.ngrok-free.dev'
).split(',')

# =========================================================
# APPLICATION DEFINITION
# =========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # for number formatting in templates

    # Local apps
    'accounts',
    'products',
    'cart',
    'orders',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # must come after Session, before Common — enables i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                # Custom context processor to expose cart info everywhere
                'cart.context_processors.cart_summary',
                'products.context_processors.categories_menu',
                'products.context_processors.wishlist_ids',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_project.wsgi.application'
ASGI_APPLICATION = 'ecommerce_project.asgi.application'

# =========================================================
# DATABASE
# Default: SQLite (zero-config). Switch to MySQL by setting env vars.
# =========================================================
USE_MYSQL = os.environ.get('USE_MYSQL', 'False') == 'True'

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'ecommerce_db'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =========================================================
# PASSWORD VALIDATION
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================================
# INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Multi-language support: English, Russian, Uzbek (Latin script)
LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
    ('uz', "O'zbekcha"),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# =========================================================
# STATIC & MEDIA FILES
# =========================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================
# AUTH
# =========================================================
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'products:home'
LOGOUT_REDIRECT_URL = 'products:home'

# =========================================================
# EMAIL (console backend for development / password reset)
# =========================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@ecommerce.local'

# =========================================================
# MESSAGES FRAMEWORK - bootstrap-compatible alert tags
# =========================================================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Pagination default
PRODUCTS_PER_PAGE = 12
