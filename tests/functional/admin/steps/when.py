"""Admin when steps."""
from pytest_bdd import when


@when('I go to instance list admin page')
def i_go_to_instance_list_admin_page(browser, base_url):
    """I go to instance list admin page."""
    browser.visit(base_url + '/core/instance/')


@when('I go to add instance admin page')
def i_go_to_add_instance_admin_page(browser, base_url):
    """I go to add instance admin page."""
    browser.visit(base_url + '/core/instance/add')


@when('I fill instance form')
def i_fill_instance_form(browser, ci_project, instance__name):
    """I fill instance form."""
    browser.fill_form({
        'name': instance__name,
        'ci_project': ci_project.id,
    })


@when('I submit the form')
def i_submit_the_form(browser):
    """I submit the form."""
    browser.find_by_css('input[type=submit]').click()
