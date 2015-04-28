"""
Django settings for pdt project.

Generated by 'django-admin startproject' using Django 1.8a1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from YamJam import yamjam

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&4qvlp7z%qqka*-_3@zk733xenawadi@1+4%7=l%dg@0ma(sr8'

# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_auth_fogbugz',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'pdt.core',
    'pdt.api',
    'django_ace',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'pdt.urls'

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

WSGI_APPLICATION = 'pdt.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_fogbugz.backend.FogBugzBackend',
)

AUTH_FOGBUGZ_SERVER = FOGBUGZ_URL = 'https://fogbugz.example.com'

AUTH_FOGBUGZ_AUTO_CREATE_USERS = True

AUTH_FOGBUGZ_ENABLE_PROFILE = True

AUTH_FOGBUGZ_ENABLE_PROFILE_TOKEN = True

SESSION_COOKIE_AGE = 1209600  # (2 weeks, in seconds)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'ORDERING_PARAM': 'order_by'
}

ATOMIC_REQUESTS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': (
            os.path.join(BASE_DIR, 'templates'),
        ),
        'OPTIONS': {
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'settings_context_processor.context_processors.settings',
                "django.core.context_processors.request",
            )
        }
    }
]

GRAPPELLI_ADMIN_TITLE = 'Paylogic deployment tool'
GRAPPELLI_INDEX_DASHBOARD = 'pdt.dashboard.CustomIndexDashboard'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_VISIBLE_SETTINGS = (
    'VERSION',
)

with open(os.path.join(BASE_DIR, 'VERSION')) as fd:
    VERSION = fd.read().strip()

try:
    from .settings_local import *
except ImportError:
    pass


cfg = yamjam('/etc/pdt/config.yaml;./config.yaml')

yam_config = cfg['pdt']

DJANGO_SECRET_KEY = yam_config['django_secret_key']

RAVEN_CONFIG = {
    'dsn': yam_config['raven']['dsn']
}

API_TOKEN = yam_config['api']['token']

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

dbcfg = yam_config['database']

DATABASES = {
    'default': {
        'ENGINE': dbcfg['engine'],
        'NAME': dbcfg['name'],
        'USER': dbcfg['user'],
        'PASSWORD': dbcfg['password'],
        'HOST': dbcfg['host'],
        'PORT': dbcfg['port'],
    }
}

# Token to use for fogbugz communication
FOGBUGZ_TOKEN = yam_config['fogbugz']['token']
FOGBUGZ_CI_PROJECT_FIELD_ID = yam_config['fogbugz']['ci_project_field_id']
AUTH_FOGBUGZ_SERVER = FOGBUGZ_URL = yam_config['fogbugz']['url']

TEMPLATE_DEBUG = DEBUG = yam_config['debug']

ALLOWED_HOSTS = ['.{0}'.format(yam_config['hostname'])] if yam_config['hostname'] else []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
