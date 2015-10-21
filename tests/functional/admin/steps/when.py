"""Admin when steps."""
from pytest_bdd import when


@when('I go to instance list admin page')
def i_go_to_instance_list_admin_page(browser, base_url):
    """I go to instance list admin page."""
    browser.visit(base_url + '/core/instance/')


@when('I go to case list admin page')
def i_go_to_case_list_admin_page(browser, base_url):
    """I go to case list admin page."""
    browser.visit(base_url + '/core/case/')


@when('I go to add instance admin page')
def i_go_to_add_instance_admin_page(browser, base_url):
    """I go to add instance admin page."""
    browser.visit(base_url + '/core/instance/add')


@when('I go to add case admin page')
def i_go_to_add_case_admin_page(browser, base_url):
    """I go to add case admin page."""
    browser.visit(base_url + '/core/case/add')


@when('I fill instance form')
def i_fill_instance_form(browser, ci_project, instance__name):
    """I fill instance form."""
    browser.fill_form({
        'name': instance__name,
    })
    browser.find_by_id('id_ci_projects-autocomplete').type('{0}'.format(ci_project.id))
    browser.find_by_xpath('//a[@class="ui-corner-all" and text()="{0}"]'.format(ci_project.name)).click()


@when('I fill case form')
def i_fill_case_form(browser, ci_project, release, case__id, case__title, case__revision):
    """I fill case form."""
    browser.fill_form({
        'id': case__id,
        'title': case__title,
        'revision': case__revision,
    })
    browser.find_by_id('id_ci_project-autocomplete').type('{0}'.format(ci_project.id))
    browser.find_by_xpath('//a[@class="ui-corner-all" and text()="{0}"]'.format(ci_project.name)).click()
    browser.find_by_id('id_release-autocomplete').type('{0}'.format(release.id))
    browser.find_by_xpath('//a[@class="ui-corner-all" and starts-with(text(), "{0}:")]'.format(release.number)).click()


@when('I submit the form')
def i_submit_the_form(browser):
    """I submit the form."""
    browser.find_by_css('input[type=submit]').click()
