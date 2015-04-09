"""WSGI endpoint tests."""

from django.core.wsgi import WSGIHandler

from pdt.wsgi import application


def test_application():
    """Test wsgi application."""
    assert isinstance(application, WSGIHandler)
