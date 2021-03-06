"""
Django settings for pdt project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from datetime import timedelta
from YamJam import yamjam

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_auth_fogbugz',
    'reversion',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'post_office',
    'pdt.core',
    'pdt.api',
    'django_ace',
    'django_object_actions',
    'adminplus',
    'taggit',
    'taggit_helpers',
    'constance',
    'constance.backends.database',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'pdt.urls'

WSGI_APPLICATION = 'pdt.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('en', _('English')),
)

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

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

EMAIL_BACKEND = 'post_office.EmailBackend'

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

_TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

cfg = yamjam('/etc/pdt/config.yaml;./config.yaml')
yam_config = cfg['pdt']

DEBUG = yam_config['debug']

import os

if DEBUG and not os.environ.get('TESTING'):
    INSTALLED_APPS += ('debug_toolbar', )

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda x: DEBUG,
    "SHOW_COLLAPSED": True,
    "RENDER_PANELS": True
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
            ),
            'loaders': [
                ('django.template.loaders.cached.Loader', _TEMPLATE_LOADERS),
            ] if not DEBUG else _TEMPLATE_LOADERS,
            'debug': DEBUG
        }
    }
]

TEMPLATE_VISIBLE_SETTINGS = (
    'VERSION',
    'FOGBUGZ_URL',
)

with open(os.path.join(BASE_DIR, 'VERSION')) as fd:
    VERSION = fd.read().strip()

try:
    from .settings_local import *
except ImportError:
    pass


SECRET_KEY = yam_config['django_secret_key']

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
        'OPTIONS': {
            'timeout': 60
        } if 'sqlite3' in dbcfg['engine'] else {}
    }
}

celery_cfg = yam_config['celery']

# Broker settings.
BROKER_URL = celery_cfg['broker_url']

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = celery_cfg['result_backend']
CELERY_ANNOTATIONS = {
    'pdt.core.tasks.update_case_from_fogbugz': {'rate_limit': '60/s'},
    'pdt.core.tasks.update_case_to_fogbugz': {'rate_limit': '60/s'}
}
BROKER_TRANSPORT_OPTIONS = {
    'fanout_prefix': True,
    'fanout_patterns': True,
    'visibility_timeout': 43200
}
CELERY_REDIS_SCHEDULER_URL = celery_cfg['scheduler_url']
ONCE_REDIS_URL = celery_cfg['scheduler_url']
ONCE_DEFAULT_TIMEOUT = 60 * 60
CELERY_REDIS_SCHEDULER_KEY_PREFIX = 'tasks:meta:'
CELERYD_LOG_COLOR = False
CELERYBEAT_SCHEDULE = {
    'fetch_cases': {
        'task': 'pdt.core.tasks.fetch_cases',
        'schedule': timedelta(hours=1),
        'args': ()
    },
    'update_cases_from_fogbugz': {
        'task': 'pdt.core.tasks.update_cases_from_fogbugz',
        'schedule': timedelta(hours=1),
        'args': ()
    },
    'update_cases_to_fogbugz': {
        'task': 'pdt.core.tasks.update_cases_to_fogbugz',
        'schedule': timedelta(hours=1),
        'args': ()
    },
    'send_emails': {
        'task': 'pdt.core.tasks.send_emails',
        'schedule': timedelta(minutes=1),
        'args': (),
    }
}
CELERY_TIMEZONE = 'UTC'
# Token to use for fogbugz communication
FOGBUGZ_TOKEN = yam_config['fogbugz']['token']
FOGBUGZ_CI_PROJECT_FIELD_ID = yam_config['fogbugz']['ci_project_field_id']
FOGBUGZ_MIGRATION_URL_FIELD_ID = yam_config['fogbugz']['migration_url_field_id']
FOGBUGZ_REVISION_FIELD_ID = yam_config['fogbugz']['revision_field_id']
AUTH_FOGBUGZ_SERVER = FOGBUGZ_URL = yam_config['fogbugz']['url']

ALLOWED_HOSTS = ['.{0}'.format(yam_config['hostname'])] if yam_config['hostname'] else []

HOST_NAME = yam_config['hostname']

cache_redis_config = yam_config['cache']['redis']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['sentry', 'syslog', 'console'],
    },
    'formatters': {
        'verbose': {
            'format': 'pdt[%(process)d]: %(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'django': {
            'format': 'pdt[%(process)d]: %(levelname)s: %(name)s: %(message)s',
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
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local7',
            'formatter': 'django',
            'address': '/dev/log'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'syslog'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'syslog'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'syslog'],
            'propagate': False,
        },
    },
}

CONSTANCE_CONFIG = {
    'TAGS_FOR_UNMERGED_CASES': ('unmerged, removed', 'Tags for unmerged cases'),
    'RELEASE_NOTES_TITLE': ('Release notes', 'Release notes title'),
    'RELEASE_NOTES_DISCLAIMER': ("""
        <li>
            The release notes are maintained by the Operational IT team, so if you have comments or suggestions feel free to <a href="mailto:opit@example.com">contact them</a>.
        </li>
    """, 'Release notes disclaimer')
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{0}:{1}'.format(cache_redis_config['host'], cache_redis_config['port']),
        'OPTIONS': {
            'DB': cache_redis_config['db'],
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 50,
                    'timeout': 20,
            }
        },
    },
}

CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

GRAPPELLI_ADMIN_TITLE = 'Paylogic deployment tool v {version}'.format(version=VERSION)
GRAPPELLI_INDEX_DASHBOARD = 'pdt.dashboard.CustomIndexDashboard'
