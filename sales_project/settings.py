# sales_app

"""
Django settings for sales_project project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import dj_database_url
from pathlib import Path
import os
from django.contrib.messages import constants as messages

# AUTH_USER_MODEL = 'sales_app.AdminUser'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!l6x2j9k=odhj^v&of$lm!#&4&ld6&jw3ol9v%5ymu!#)w##xs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'corsheaders',
     'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sales_app',
    'mathfilters'
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this line
    'corsheaders.middleware.CorsMiddleware',  # Add this line at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sales_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'sales_app/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CORS_ALLOW_ALL_ORIGINS = True  # Allow all domains


WSGI_APPLICATION = 'sales_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'sm',  # Your database name
#         'USER': 'postgres',     # Your PostgreSQL username
#         'PASSWORD': '123',  # Your PostgreSQL password
#         'HOST': 'localhost',    # Localhost since PostgreSQL is on your machine
#         'PORT': '5432',         # Default PostgreSQL port
#     }
# }


DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://sales_db_fuyp_user:NZ1lgH9EqBdLm90yZLNhvV5js6l0es8I@dpg-cv7sm6dds78s73cps09g-a.singapore-postgres.render.com/sales_db_fuyp',
        conn_max_age=600
    )
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'sales_app/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Use your SMTP provider's host
EMAIL_PORT = 587  # Use 465 for SSL or 587 for TLS
EMAIL_USE_TLS = True  # Use SSL if using port 465
EMAIL_HOST_USER = "abhism574@gmail.com"  # Your email address
EMAIL_HOST_PASSWORD = "cyrz tgiv hmkq jqjq"  # App password (not your Gmail password)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

RAZORPAY_KEY_ID = 'rzp_test_JFfuEOzEhk0RSb'
RAZORPAY_KEY_SECRET = 'uyt4Z9KU5gegVZvufZxqgUtN'



MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
