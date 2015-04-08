"""PDT tests configuration."""
import datetime

import mock

import factory
import pytest

from pdt.core.models import (
    CIProject,
    Instance,
    Case,
    Release,
)


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


@pytest.fixture
def ci_project_name():
    """CI Project name."""
    return 'test-ci-project'


@pytest.fixture
def ci_project_description():
    """CI Project description."""
    return 'Test ci project description'


@pytest.fixture
def ci_project(db, ci_project_name, ci_project_description):
    """CI project."""
    return CIProject.objects.create(name=ci_project_name, description=ci_project_description)


@pytest.fixture
def instance_name():
    """Instance name."""
    return 'staging'


@pytest.fixture
def instance_description():
    """Instance description."""
    return 'Staging instance'


@pytest.fixture
def instance(instance_name, instance_description, ci_project):
    """CI project."""
    return Instance.objects.create(ci_project=ci_project, name=instance_name, description=instance_description)


@pytest.fixture
def release_name():
    """Release name."""
    return '1504'


@pytest.fixture
def release_date():
    """Release date."""
    return datetime.date(year=2015, month=1, day=1)


@pytest.fixture
def release(release_name, release_date):
    """Release."""
    return Release.objects.create(name=release_name, date=release_date)


@pytest.fixture
def case_id():
    """Case id."""
    return 33322


@pytest.fixture
def case_title():
    """Case title."""
    return 'Some case title'


@pytest.fixture
def case_description():
    """Case description."""
    return 'Some case description'


@pytest.fixture
def case(case_id, case_title, case_description, ci_project, release):
    """Case."""
    return Case.objects.create(
        id=case_id, title=case_title, description=case_description, ci_project=ci_project, release=release)


@pytest.yield_fixture(autouse=True)
def mocked_fogbugz(monkeypatch):
    """Mock Fogbugz class to avoid external connections."""
    mocked_fogbugz = mock.patch('fogbugz.FogBugz')
    yield mocked_fogbugz.start()
    mocked_fogbugz.stop()


class ReleaseFactory(factory.django.DjangoModelFactory):

    """Release factory."""

    name = factory.Sequence(lambda n: 'release-{0}'.format(n))

    class Meta:
        model = 'core.Release'


class CaseFactory(factory.django.DjangoModelFactory):

    """Case factory."""

    id = factory.Sequence(lambda n: n)

    class Meta:
        model = 'core.Case'

    release = factory.SubFactory(ReleaseFactory)
    ci_project = factory.SubFactory('tests.conftest.CIProjectFactory')


class MigrationFactory(factory.django.DjangoModelFactory):

    """Migration factory."""

    uid = factory.Sequence(lambda n: 'asdfasdf2342{0}'.format(n))

    class Meta:
        model = 'core.Migration'

    case = factory.SubFactory(CaseFactory)


class CIProjectFactory(factory.django.DjangoModelFactory):

    """CIProject factory."""

    name = factory.Sequence(lambda n: 'ci-project-{0}'.format(n))

    class Meta:
        model = 'core.CIProject'


class InstanceFactory(factory.django.DjangoModelFactory):

    """Instance factory."""

    name = factory.Sequence(lambda n: 'instance-{0}'.format(n))

    class Meta:
        model = 'core.Instance'

    ci_project = factory.SubFactory(CIProjectFactory)


class MigrationReportFactory(factory.django.DjangoModelFactory):

    """MigrationReport factory."""

    class Meta:
        model = 'core.MigrationReport'

    instance = factory.SubFactory(InstanceFactory)
    migration = factory.SubFactory(
        MigrationFactory, case__ci_project=factory.SelfAttribute('...instance.ci_project'))


@pytest.fixture
def migration_report_factory():
    """Migration report factory."""
    return MigrationReportFactory


@pytest.fixture
def migration_factory():
    """Migration factory."""
    return MigrationFactory
