"""
WSGI config for pdt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdt.settings_deployment")

from django.core.wsgi import get_wsgi_application  # NOQA
application = get_wsgi_application()
