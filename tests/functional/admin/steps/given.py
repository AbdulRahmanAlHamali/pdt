"""Admin given steps."""
from pytest_bdd import given, parsers


@given('I have an instance')
def i_have_an_instance(db, instance):
    """I have an instance."""
    return instance


@given(parsers.parse('I am {user_role}'))
def i_am(user_role):
    """I have an instance."""
    return user_role
