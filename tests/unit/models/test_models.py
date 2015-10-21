"""Test core models."""
import mock
import pytest

from pdt.core.models import Case


@pytest.mark.django_db
def test_get_or_create_case(mocked_fogbugz, release):
    """Test get_or_create_from_fogbugz Case method."""
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = str(release.number)
    mocked_case.dtfixfor.string = str(release.datetime)
    mocked_case.dtlastupdated.string = str(release.datetime)
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = 'ci-project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    mocked_case.revision.string = '123123'
    case, created = Case.objects.get_or_create_from_fogbugz(case_id=1234)
    assert case.release.datetime == release.datetime
    assert created
    assert case.revision == '123123'


@pytest.mark.django_db
def test_migration_report_unicode(migration_report_factory):
    """Test migration report unicode."""
    migration_report = migration_report_factory()
    assert str(migration_report) == '{self.migration}: {self.instance}: {self.datetime}: {status}'.format(
        self=migration_report, status=migration_report.get_status_display())


@pytest.mark.django_db
def test_migration_step_report_unicode(migration_report_factory):
    """Test migration step report unicode."""
    migration_step_report = migration_report_factory().step_reports.first()
    assert str(migration_step_report) == '{self.report}: {self.step}: {self.datetime}: {status}'.format(
        self=migration_step_report, status=migration_step_report.get_status_display())


@pytest.mark.django_db
def test_deployment_report_unicode(deployment_report):
    """Test deployment report unicode."""
    assert str(deployment_report) == '{self.id}: {self.instance}: {self.datetime}: {status}'.format(
        self=deployment_report, status=deployment_report.get_status_display())


@pytest.mark.django_db
@mock.patch('post_office.mail.send')
def test_deloyment_report_email(mocked_send, deployment_report_factory, case):
    """Test migration report email notice."""
    report = deployment_report_factory(cases=[case])
    notification_template = report.instance.notification_template
    mocked_send.assert_called_once_with(
        template=notification_template.template.name,
        sender=notification_template.from_email, context={'deployment_report': report},
        recipients=notification_template.to)
