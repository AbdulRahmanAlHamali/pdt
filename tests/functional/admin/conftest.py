"""Admin functional tests configuration."""
from tests.functional.admin.steps.given import *
from tests.functional.admin.steps.when import *
from tests.functional.admin.steps.then import *

import pytest


@pytest.fixture
def user_role():
    """User role."""
    return 'superuser'


@pytest.fixture
def base_url(connection_closer, live_server):
    """Base url."""
    connection_closer()
    return live_server.url


@pytest.fixture
def connection_closer():
    """DB connection closer function."""
    def closer():
        from django.db import connections
        for conn in connections.all():
            conn.close()
    return closer


@pytest.fixture
def browser(request, user_role, browser, admin_user, base_url):
    """Pre-log in with given user role."""
    browser.visit(base_url + '/login/')
    browser.fill_form({
        'username': admin_user.username,
        'password': 'password'
    })
    browser.find_by_css('input[type=submit]').click()
    return browser
