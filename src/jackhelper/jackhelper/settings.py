import os
from pathlib import Path

from . import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'auth.apps.AuthConfig',
    'main.apps.MainConfig',
    'stats.apps.StatsConfig',
    'plans.apps.PlansConfig',
    'orders.apps.OrdersConfig',
    'salaries.apps.SalariesConfig',

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'jackhelper.middleware.ExceptionMiddleware',
    'auth.middleware.AuthMiddleware',
]

ROOT_URLCONF = 'jackhelper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/errors'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'jackhelper.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=main'
        },
        'HOST': config.DB_HOST,
        'PORT' : config.DB_PORT,
        'NAME': config.DB_NAME,
        'USER': config.DB_USER,
        'PASSWORD': config.DB_PASS,
    },
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}",
    }
}


# Internationalization
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'auth/static'),
    os.path.join(BASE_DIR, 'main/static'),
    os.path.join(BASE_DIR, 'stats/static'),
    os.path.join(BASE_DIR, 'plans/static'),
    os.path.join(BASE_DIR, 'orders/static'),
    os.path.join(BASE_DIR, 'salaries/static'),
]
if DEBUG is False:
    STATIC_ROOT = 'static'
else:
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'static'))

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400 * 30 # 30 days

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"