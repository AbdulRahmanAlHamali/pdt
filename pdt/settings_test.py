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
TEMPLATE_DEBUG = DEBUG
