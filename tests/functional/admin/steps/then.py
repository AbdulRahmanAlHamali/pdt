"""Admin then steps."""
from pytest_bdd import then, parsers

from pdt.core.models import (
    Case,
    CIProject,
    Instance,
    Migration,
)


@then('I should see an instance in the list')
def i_should_see_an_instance_in_the_list(browser, instance):
    """I should see an instance in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(instance.name))


@then('I should see a case in the list')
def i_should_see_a_case_in_the_list(browser, case):
    """I should see a case in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(case.id))


@then('I should see a ci project in the list')
def i_should_see_a_ci_project_in_the_list(browser, ci_project):
    """I should see a ci project in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(ci_project.name))


@then('I should see a migration in the list')
def i_should_see_a_migration_in_the_list(browser, migration):
    """I should see a migration in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(migration.uid))


@then(parsers.parse('I should see a "{message_type}" message'))
def i_should_see_a_message(browser, message_type):
    """I should see a message."""
    assert browser.find_by_xpath('//ul[contains(@class, "messagelist")]/li[contains(@class, "{0}")]'.format(
        message_type))


@then(parsers.parse('the instance should be created'))
def instance_should_be_created(browser, instance__name):
    """Instance should be created."""
    assert Instance.objects.get(name=instance__name)


@then(parsers.parse('the case should be created'))
def case_should_be_created(browser, case__id):
    """Case should be created."""
    assert Case.objects.get(id=case__id)


@then(parsers.parse('the ci project should be created'))
def ci_project_should_be_created(browser, ci_project__name):
    """CI project should be created."""
    assert CIProject.objects.get(name=ci_project__name)


@then(parsers.parse('the migration should be created'))
def migration_should_be_created(browser, migration__uid):
    """Migration should be created."""
    assert Migration.objects.get(uid=migration__uid)
