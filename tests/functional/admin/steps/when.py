"""Admin when steps."""
from pytest_bdd import when


@when('I go to instance list admin page')
def i_go_to_instance_list_admin_page(browser, base_url):
    """I go to instance list admin page."""
    browser.visit(base_url + '/admin/')
