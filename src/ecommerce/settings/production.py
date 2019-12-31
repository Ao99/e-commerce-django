from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['d626b1ba14904b5d83f341340ce1dfc5.vfs.cloud9.ca-central-1.amazonaws.com', 'ecommerce.ca-central-1.elasticbeanstalk.com']


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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


# stripe

STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')