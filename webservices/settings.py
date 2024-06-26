"""
Django settings for webservices project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    load_dotenv(dotenv_file)


def get_secret(key: str) -> str:
    try:
        # environment variable first
        return os.environ[key]
    except KeyError:
        # raise exception in case when can't find key
        # in secret_data or environment variables
        error_msg = 'Set the {} environment variable'.format(key)
        raise ImproperlyConfigured(error_msg)


def get_bool_secret(key: str) -> bool:
    return bool(int(get_secret(key)))


def get_host(url: str) -> str:
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY')

ENVIRONMENT = get_secret('ENV')
ENV_DEV = 'dev'
ENV_PROD = 'production'
ENV_LOCAL = 'local'
IS_LOCAL = ENVIRONMENT == ENV_LOCAL

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_secret('DEBUG')

API_URL = get_secret('API_URL')
SITE_URL = get_secret('SITE_URL')
ADMIN_EMAIL = get_secret('ADMIN_EMAIL')
SEND_EMAILS = get_bool_secret('SEND_EMAILS')
EMAIL_BACKEND = 'django_ses.SESBackend'

AUTH_USER_MODEL = 'authentication.User'

# TODO
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    # TODO
    # 'django_celery_beat',
    'django_celery_results',
    'django_filters',
]
MY_APPS = ['authentication']
INSTALLED_APPS += MY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS
# look here: https://pypi.org/project/django-cors-headers/
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [get_host(API_URL), get_host(SITE_URL)]
CSRF_TRUSTED_ORIGINS = [get_host(API_URL), get_host(SITE_URL)]

ROOT_URLCONF = 'webservices.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'webservices.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# TODO: maybe add a test database for simulation?
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'HOST': get_secret('DB_HOST'),
        'PORT': get_secret('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# CACHE
# http://niwinz.github.io/django-redis/latest/
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{redis_host}:{redis_port}/1'.format(
            redis_host=get_secret('REDIS_HOST'), redis_port=get_secret('REDIS_PORT')
        ),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 1000},
        },
    }
}

# REST framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'webservices.paginators.StandardPageNumberPagination',
}

# authentication
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# AWS
AWS_ACCESS_KEY_ID = get_secret('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY')

# CELERY
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#configuration
CELERY_BROKER_URL = f'sqs://{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}@'
# NOTE: this will automatically create queues unique to an environment i.e. dev-celery, production-celery
#  there is no need to create these manually in SQS, celery will create them automatically
CELERY_BROKER_TRANSPORT_OPTIONS = {"queue_name_prefix": f"{ENVIRONMENT}-"}
CELERY_TASK_DEFAULT_QUEUE = 'celery'
CELERY_TIMEZONE = 'US/Eastern'
CELERY_TASK_ACKS_LATE = True
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#django-celery-results
# SQS does not work as a result backend, so we will use the redis cache as the backend
# TODO: do we need this? seeing this on startup: results:     disabled://
CELERY_CACHE_BACKEND = 'default'
CELERY_TASK_ROUTES: dict = {}
CELERY_QUEUE_MAX_PRIORITY = 10
CELERY_TASK_TIME_LIMIT = 60 * 30  # 30 minutes
# NOTE: this will be overriden for ease of testing
CELERY_TASK_ALWAYS_EAGER = False

# TODO
#  use this for weekly digests, daily summaries for dashboards, etc.
# TASK SCHEDULER
# add this to requirements: django-celery-beat==2.4.0
# CELERY_BEAT_SCHEDULE = {}

# CHAT ENGINE
CHAT_ENGINE_BASE_URL = "https://api.chatengine.io/"
CHAT_ENGINE_PROJECT_ID = get_secret("CHAT_ENGINE_PROJECT_ID")
CHAT_ENGINE_SECRET_KEY = get_secret("CHAT_ENGINE_SECRET_KEY")

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
# TODO: figure this out
STATIC_URL = '/tmp/static/'
STATIC_ROOT = '/tmp/static/'
STATICFILE_DIRS = [STATIC_ROOT]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
