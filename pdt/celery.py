"""PDT celery integration."""
import os

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdt.settings')

from django.conf import settings

app = Celery('pdt')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if hasattr(settings, 'RAVEN_CONFIG') and settings.RAVEN_CONFIG['dsn']:
    # Celery signal registration
    client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
    register_signal(client)
