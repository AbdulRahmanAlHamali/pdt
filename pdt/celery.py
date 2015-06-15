"""PDT celery integration."""
import os

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdt.settings')

from django.conf import settings  # NOQA

app = Celery('pdt')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if hasattr(settings, 'RAVEN_CONFIG'):
    # Celery signal registration
    try:
        client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
        register_signal(client)
    except ValueError:
        pass
