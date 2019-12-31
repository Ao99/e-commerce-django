from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['ip-address', 'www.your-website.com']


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': '',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# stripe

STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')