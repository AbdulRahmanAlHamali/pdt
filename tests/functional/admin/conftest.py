"""Admin functional tests configuration."""
from tests.functional.admin.steps.given import *
from tests.functional.admin.steps.when import *
from tests.functional.admin.steps.then import *

import pytest


@pytest.fixture
def user_role():
    """User role."""
    return 'superuser'


@pytest.fixture(autouse=True)
def base_url(live_server):
    """Base url."""
    return live_server.url


@pytest.fixture
def instance__name(faker):
    """Instance name."""
    return 'instance - {0}'.format(faker.md5())


@pytest.fixture
def case__id(faker):
    """Case id."""
    return faker.pyint()


@pytest.fixture
def case__title(faker):
    """Case title."""
    return faker.text(max_nb_chars=255)


@pytest.fixture
def case__revision(faker):
    """Case revision."""
    return faker.md5()


@pytest.fixture
def ci_project__name(faker):
    """CI project name."""
    return 'CI project - {0}'.format(faker.md5())


@pytest.fixture
def ci_project__description(faker):
    """CI project description."""
    return faker.text(max_nb_chars=255)


@pytest.fixture
def browser(base_url, request, user_role, admin_user, browser):
    """Pre-log in with given user role."""
    browser.visit(base_url + '/login/')
    browser.fill_form({
        'username': admin_user.username,
        'password': 'password'
    })
    browser.find_by_css('input[type=submit]').click()
    return browser
