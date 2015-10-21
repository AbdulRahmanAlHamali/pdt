"""Admin given steps."""
from pytest_bdd import given, parsers


@given('I have an instance')
def instance(instance_factory):
    """Instance."""
    return instance_factory()

given('I have a CI project', fixture='ci_project')


@given(parsers.parse('I am {user_role}'))
def i_am(user_role):
    """I have an instance."""
    return user_role
