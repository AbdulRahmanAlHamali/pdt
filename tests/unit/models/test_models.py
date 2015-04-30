"""Test core models."""
import pytest

from pdt.core.models import Case


@pytest.mark.django_db
def test_get_or_create_case(mocked_fogbugz, release):
    """Test get_or_create_from_fogbugz Case method."""
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = release.name
    mocked_case.dtfixfor.string = str(release.datetime)
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = 'ci-project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    case, created = Case.objects.get_or_create_from_fogbugz(case_id=1234)
    assert case.release.datetime == release.datetime
    assert created


@pytest.mark.django_db
def test_migration_report_unicode(migration_report_factory):
    """Test migration report unicode."""
    migration_report = migration_report_factory()
    assert str(migration_report) == '{self.migration}: {self.instance}: {self.datetime}: {self.status}'.format(
        self=migration_report)


@pytest.mark.django_db
def test_migration_step_report_unicode(migration_report_factory):
    """Test migration step report unicode."""
    migration_step_report = migration_report_factory().step_reports.first()
    assert str(migration_step_report) == '{self.report}: {self.step}: {self.datetime}: {self.status}'.format(
        self=migration_step_report)


@pytest.mark.django_db
def test_deployment_report_unicode(deployment_report):
    """Test deployment report unicode."""
    assert str(deployment_report) == '{self.release}: {self.instance}: {self.datetime}'.format(self=deployment_report)
