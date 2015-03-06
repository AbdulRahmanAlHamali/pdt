"""Build settings."""
from .settings import *

DATABASES.update({
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'pdt',
    }
})
