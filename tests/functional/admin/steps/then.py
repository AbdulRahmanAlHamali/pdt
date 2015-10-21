"""Admin then steps."""
from pytest_bdd import then, parsers

from pdt.core.models import (
    Case,
    Instance,
)


@then('I should see an instance in the list')
def i_should_see_an_instance_in_the_list(browser, instance):
    """I should see an instance in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(instance.name))


@then('I should see a case in the list')
def i_should_see_a_case_in_the_list(browser, case):
    """I should see a case in the list."""
    assert browser.find_by_xpath('//table[@id="result_list"]//tr//*[text()="{0}"]'.format(case.id))


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
