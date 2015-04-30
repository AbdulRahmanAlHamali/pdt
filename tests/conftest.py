"""PDT tests configuration."""
import mock

import factory.fuzzy
from faker import Factory

import pytest
import py
from pytest_factoryboy import register

from pdt.core.models import MigrationStep

fake = Factory.create()


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

    name = factory.fuzzy.FuzzyText(prefix='release-')

    class Meta:
        model = 'core.Release'


@register
class CIProjectFactory(factory.django.DjangoModelFactory):

    """CIProject factory."""

    name = factory.fuzzy.FuzzyText(prefix='ci-project-')

    class Meta:
        model = 'core.CIProject'


@register
class CaseFactory(factory.django.DjangoModelFactory):

    """Case factory."""

    id = factory.fuzzy.FuzzyInteger(10000, 40000)

    class Meta:
        model = 'core.Case'

    release = factory.SubFactory(ReleaseFactory)
    ci_project = factory.SubFactory(CIProjectFactory)


class MigrationStepFactory(factory.django.DjangoModelFactory):

    """Migration step factory."""

    position = factory.Sequence(lambda n: n)
    type = factory.fuzzy.FuzzyChoice(type_ for type_, _ in MigrationStep.TYPE_CHOICES)
    code = factory.LazyAttribute(lambda o: fake.text())
    migration = factory.SubFactory('tests.conftest.MigrationFactory')


class PreDeployMigrationStepFactory(MigrationStepFactory):

    """PreDeployMigrationStep factory."""

    class Meta:
        model = 'core.PreDeployMigrationStep'


class PostDeployMigrationStepFactory(MigrationStepFactory):

    """PostDeployMigrationStep factory."""

    class Meta:
        model = 'core.PostDeployMigrationStep'


@register
class MigrationFactory(factory.django.DjangoModelFactory):

    """Migration factory."""

    uid = factory.fuzzy.FuzzyText(length=42)
    reviewed = False

    class Meta:
        model = 'core.Migration'

    case = factory.SubFactory(CaseFactory)
    pre_deploy_steps = factory.RelatedFactory(PreDeployMigrationStepFactory, 'migration')
    post_deploy_steps = factory.RelatedFactory(PostDeployMigrationStepFactory, 'migration')


@register
class InstanceFactory(factory.django.DjangoModelFactory):

    """Instance factory."""

    name = factory.fuzzy.FuzzyText(prefix='instance-')

    class Meta:
        model = 'core.Instance'

    ci_project = factory.SubFactory(CIProjectFactory)


class MigrationStepReportFactory(factory.django.DjangoModelFactory):

    """MigrationStepReport factory."""

    class Meta:
        model = 'core.MigrationStepReport'

    step = factory.LazyAttribute(lambda o: o.report.migration.pre_deploy_steps.first())


@register
class MigrationReportFactory(factory.django.DjangoModelFactory):

    """MigrationReport factory."""

    class Meta:
        model = 'core.MigrationReport'

    instance = factory.SubFactory(InstanceFactory)
    migration = factory.SubFactory(
        MigrationFactory, case__ci_project=factory.SelfAttribute('...instance.ci_project'))
    step_reports = factory.RelatedFactory(MigrationStepReportFactory, 'report')


@register
class DeploymentReportFactory(factory.django.DjangoModelFactory):

    """DeploymentReport factory."""

    class Meta:
        model = 'core.DeploymentReport'

    instance = factory.SubFactory(InstanceFactory)
    release = factory.SubFactory(ReleaseFactory)
