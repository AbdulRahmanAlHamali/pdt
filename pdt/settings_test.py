"""Build settings."""
from .settings import *

DATABASES.update({
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'pdt',
    }
})

RAVEN_CONFIG = {
    'dsn': None
}

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
CELERY_ALWAYS_EAGER = True
BROKER_URL = 'memory://'
CELERY_CACHE_BACKEND = 'memory'
BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
FOGBUGZ_CI_PROJECT_FIELD_ID = 'cixproject'
FOGBUGZ_MIGRATION_URL_FIELD_ID = 'dbxmigration'
FOGBUGZ_REVISION_FIELD_ID = 'revision'

LOGGING = None
