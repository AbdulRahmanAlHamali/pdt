"""PDT tests configuration."""
import mock

import factory
import pytest
import py
from pytest_factoryboy import register


@pytest.fixture
def project_path():
    """Project path."""
    return py.path.local(__file__).dirname().dirname()


class EqualsAny(object):

    """Helper object comparison to which is always 'equal'."""

    def __init__(self, type_=None):
        """Initialize new instance."""
        self.type = type_

    def __eq__(self, other):
        """True if the type is correct."""
        return isinstance(other, self.type) if self.type else True

    def __cmp__(self, other):
        """0 if the type is correct."""
        return 0 if (isinstance(other, self.type) if self.type else False) else -1


@pytest.fixture
def equals_any():
    """Helper for assertions to always succeed."""
    return EqualsAny()


@pytest.yield_fixture(autouse=True)
def mocked_fogbugz(monkeypatch):
    """Mock Fogbugz class to avoid external connections."""
    mocked_fogbugz = mock.patch('fogbugz.FogBugz')
    yield mocked_fogbugz.start()
    mocked_fogbugz.stop()


@register
class ReleaseFactory(factory.django.DjangoModelFactory):

    """Release factory."""

    name = factory.Sequence(lambda n: 'release-{0}'.format(n))

    class Meta:
        model = 'core.Release'


@register
class CIProjectFactory(factory.django.DjangoModelFactory):

    """CIProject factory."""

    name = factory.Sequence(lambda n: 'ci-project-{0}'.format(n))

    class Meta:
        model = 'core.CIProject'


@register
class CaseFactory(factory.django.DjangoModelFactory):

    """Case factory."""

    id = factory.Sequence(lambda n: n)

    class Meta:
        model = 'core.Case'

    release = factory.SubFactory(ReleaseFactory)
    ci_project = factory.SubFactory(CIProjectFactory)


@register
class MigrationFactory(factory.django.DjangoModelFactory):

    """Migration factory."""

    uid = factory.Sequence(lambda n: 'asdfasdf2342{0}'.format(n))

    class Meta:
        model = 'core.Migration'

    case = factory.SubFactory(CaseFactory)


@register
class InstanceFactory(factory.django.DjangoModelFactory):

    """Instance factory."""

    name = factory.Sequence(lambda n: 'instance-{0}'.format(n))

    class Meta:
        model = 'core.Instance'

    ci_project = factory.SubFactory(CIProjectFactory)


@register
class MigrationReportFactory(factory.django.DjangoModelFactory):

    """MigrationReport factory."""

    class Meta:
        model = 'core.MigrationReport'

    instance = factory.SubFactory(InstanceFactory)
    migration = factory.SubFactory(
        MigrationFactory, case__ci_project=factory.SelfAttribute('...instance.ci_project'))


@register
class DeploymentReportFactory(factory.django.DjangoModelFactory):

    """DeploymentReport factory."""

    class Meta:
        model = 'core.DeploymentReport'

    instance = factory.SubFactory(InstanceFactory)
    release = factory.SubFactory(ReleaseFactory)
