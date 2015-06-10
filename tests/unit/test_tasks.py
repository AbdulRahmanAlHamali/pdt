"""Test PDT tasks."""
import mock

from pdt.core.tasks import (
    notify_deployed_cases,
    notify_migrated_cases,
)
from pdt.core.models import (
    DeploymentReport,
    MigrationReport,
)


@mock.patch('pdt.core.tasks.update_case_to_fogbugz.apply_async')
def test_notify_deployed_cases(mocked_update_case_to_fogbugz, db, case_factory, deployment_report_factory, instance):
    """Test notify deployed cases task."""
    deployed_case = case_factory(tags=['deployed-{0}'.format(instance.name)], ci_project=instance.ci_project)
    deployment_report_factory(
        status=DeploymentReport.STATUS_DEPLOYED,
        instance=instance)
    not_deployed_case = case_factory(ci_project=instance.ci_project)
    deployment_report_factory(
        status=DeploymentReport.STATUS_DEPLOYED,
        instance=instance)
    new_report = deployment_report_factory(
        status=DeploymentReport.STATUS_DEPLOYED,
        instance=instance)
    deployed_case.edits.all().delete()
    not_deployed_case.edits.all().delete()
    mocked_update_case_to_fogbugz.reset_mock()
    notify_deployed_cases()
    edits = not_deployed_case.edits.all()
    assert len(edits) == 1
    assert edits[0].params['report'] == new_report.id
    mocked_update_case_to_fogbugz.assert_called_once_with(kwargs={'case_id': not_deployed_case.id})


@mock.patch('pdt.core.tasks.update_case_to_fogbugz.apply_async')
def test_notify_migrated_cases(
        mocked_update_case_to_fogbugz, db, case_factory, migration_factory, migration_report_factory, instance):
    """Test notify cases task."""
    migrated_case = case_factory(tags=['migration-applied-{0}'.format(instance.name)], ci_project=instance.ci_project)
    report = migration_report_factory(
        migration=migration_factory(case=migrated_case),
        status=MigrationReport.STATUS_APPLIED,
        instance=instance)
    report.status = MigrationReport.STATUS_APPLIED
    report.save()
    not_migrated_case = case_factory(ci_project=instance.ci_project)
    report = migration_report_factory(
        status=MigrationReport.STATUS_APPLIED,
        migration=migration_factory(case=not_migrated_case),
        instance=instance)
    report.status = MigrationReport.STATUS_APPLIED
    report.save()
    migrated_case.edits.all().delete()
    not_migrated_case.edits.all().delete()
    mocked_update_case_to_fogbugz.reset_mock()
    notify_migrated_cases()
    edits = not_migrated_case.edits.all()
    assert len(edits) == 1
    assert edits[0].params['instance'] == instance.id
    mocked_update_case_to_fogbugz.assert_called_once_with(kwargs={'case_id': not_migrated_case.id})
