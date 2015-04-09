"""Admin then steps."""
from pytest_bdd import then


@then('I should see an instance in the list')
def i_should_see_an_instance_in_the_list(browser):
    """I should see an instance in the list."""
    assert browser.find_by_css('li.some')
