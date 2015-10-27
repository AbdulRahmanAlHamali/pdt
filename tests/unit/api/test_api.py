"""Test public API."""
import json

from django.utils.dateparse import parse_datetime
import pytest

from pdt.core.models import (
    Case,
    CaseEdit,
    DeploymentReport,
    MigrationReport,
    MigrationStepReport,
)


def test_migration_filter_exclude_status(admin_client, migration_report_factory, equals_any):
    """Test migration filter when exclude status parameter is used."""
    mr1 = migration_report_factory(status='apl', instance__name='1')
    mr1.status = MigrationReport.STATUS_APPLIED
    mr1.save()
    mr2 = migration_report_factory(
        status=MigrationReport.STATUS_ERROR, migration=mr1.migration,
        instance__ci_projects=mr1.instance.ci_projects.all(), instance__name='2')
    applied_step_ids = {
        report.step.id for report in mr2.step_reports.all() if report.status == MigrationStepReport.STATUS_APPLIED}
    data = admin_client.get(
        '/api/migrations/', dict(
            exclude_status='apl', instance=mr1.instance.name)).data
    assert len(data) == 1
    migration = mr2.migration
    assert data[0] == {
        'id': migration.id,
        'uid': migration.uid,
        'parent': migration.parent,
        'case': {
            'id': migration.case.id,
            'title': migration.case.title,
            'description': migration.case.description,
            'ci_project': migration.case.ci_project.name
        },
        'pre_deploy_steps': [
            {'id': step.id, 'type': step.type, 'position': step.position, 'code': step.code, 'path': None}
            for step in migration.pre_deploy_steps.all() if step.id not in applied_step_ids],
        'post_deploy_steps': [
            {'id': step.id, 'type': step.type, 'position': step.position, 'code': step.code, 'path': None}
            for step in migration.post_deploy_steps.all() if step.id not in applied_step_ids],
        'final_steps': [
            {'id': step.id, 'type': step.type, 'position': step.position, 'code': step.code, 'path': None}
            for step in migration.final_steps.all() if step.id not in applied_step_ids],
        'category': migration.category,
        'reviewed': False,
        'reports': [{
            'id': mr1.id,
            'instance': {
                'id': mr1.instance.id,
                'name': mr1.instance.name,
                'description': mr1.instance.description,
                'ci_projects': [{
                    'id': migration.case.ci_project.id,
                    'name': migration.case.ci_project.name,
                    'description': migration.case.ci_project.description,
                }],
            },
            'status': mr1.status,
            'datetime': equals_any,
            'log': mr1.log
        }, {
            'id': mr2.id,
            'instance': {
                'id': mr2.instance.id,
                'name': mr2.instance.name,
                'description': mr2.instance.description,
                'ci_projects': [{
                    'id': migration.case.ci_project.id,
                    'name': migration.case.ci_project.name,
                    'description': migration.case.ci_project.description,
                }],
            },
            'status': mr2.status,
            'datetime': equals_any,
            'log': mr2.log
        }],
        'release': {
            'id': migration.case.release.id,
            'number': migration.case.release.number,
            # Ugly, but that's how rest framework does it too.
            'datetime': migration.case.release.datetime.isoformat().replace('+00:00', 'Z')
        }
    }


def test_migration_filter_status(admin_client, migration_report_factory):
    """Test migration filter when status parameter is used."""
    mr1 = migration_report_factory(status='apl')
    mr1.status = 'apl'
    mr1.save()
    migration_report_factory(
        status='err', migration=mr1.migration, instance__ci_projects=mr1.instance.ci_projects.all())
    data = admin_client.get(
        '/api/migrations/', dict(status='apl', instance=mr1.instance.name)).data
    assert len(data) == 1
    assert data[0]['id'] == mr1.migration.id


def test_migration_filter_ci_project(admin_client, migration_factory):
    """Test migration filter when CI project parameter is used."""
    migration_factory(case__ci_project__name='some-other-project')
    migration_factory(case__ci_project__name='some-project')
    data = admin_client.get(
        '/api/migrations/', dict(ci_project='some-project')).data
    assert len(data) == 1
    data = admin_client.get(
        '/api/migrations/', dict(ci_project='some-other-project')).data
    assert len(data) == 1


def test_migration_filter_reviewed(admin_client, migration_factory):
    """Test migration filter when reviewed parameter is used."""
    migration1 = migration_factory(reviewed=False)
    migration2 = migration_factory(reviewed=True)
    data = admin_client.get(
        '/api/migrations/', dict(reviewed=True)).data
    assert len(data) == 1
    assert data[0]['uid'] == migration2.uid
    data = admin_client.get(
        '/api/migrations/', dict(reviewed=False)).data
    assert len(data) == 1
    assert data[0]['uid'] == migration1.uid


def test_migration_filter_instance(admin_client, migration_report_factory, instance_factory):
    """Test migration filter when instance parameter is used."""
    mr1 = migration_report_factory()
    instance = instance_factory(ci_projects=[mr1.migration.case.ci_project])
    data = admin_client.get(
        '/api/migrations/', dict(instance=instance.name)).data
    assert len(data) == 1
    assert data[0]['uid'] == mr1.migration.uid


def test_migration_filter_release(admin_client, migration_report_factory, instance_factory, ci_project):
    """Test migration filter when instance parameter is used."""
    mr1 = migration_report_factory(migration__case__release__number='1520', migration__case__ci_project=ci_project)
    mr2 = migration_report_factory(migration__case__release__number='1510', migration__case__ci_project=ci_project)
    migration_report_factory(migration__case__release=None)
    migration_report_factory(migration__case__release__number='1530')
    data = admin_client.get(
        '/api/migrations/', dict(release=mr1.migration.case.release.number)).data
    assert len(data) == 2
    assert {data[0]['uid'], data[1]['uid']} == {mr1.migration.uid, mr2.migration.uid}


def test_create_migration_no_case(mocked_fogbugz, admin_client):
    """Test create migration when fb case is not found."""
    mocked_fogbugz.return_value.search.return_value.cases.find.return_value = None
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "parent": None,
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [],
            "post_deploy_steps": [],
            "final_steps": []
        }), content_type='application/json').data
    assert data == {'case': ["['Case with such id cannot be found']"]}


def test_create_migration_case_no_milestone(mocked_fogbugz, admin_client):
    """Test create migration when fb case doesn't have a milestone."""
    mocked_fogbugz.return_value.search.return_value.cases.find.return_value.sfixfor.string = None
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "parent": None,
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [],
            "post_deploy_steps": [],
            "final_steps": []
        }), content_type='application/json').data
    assert data == {'case': ["['Case milestone is not set']"]}


def test_create_migration(mocked_fogbugz, admin_client):
    """Test create migration."""
    case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    case.attrs = dict(ixbug='33322')
    case.sfixfor.string = '1516'
    case.dtfixfor.string = '2015-01-18T23:00:00Z'
    case.dtlastupdated.string = '2015-01-18T23:00:00Z'
    case.stitle.string = 'Some title'
    case.soriginaltitle.string = 'Some original title'
    case.cixproject.string = 'some-ci-project'
    case.sproject.string = 'Some project'
    case.sarea.string = 'Some area'
    case.revision.string = '123123'
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "parent": None,
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [
                {"type": "mysql", "code": "SELECT * from some", "position": 1},
            ],
            "post_deploy_steps": [
                {"type": "python", "code": "import some", "position": 1},
            ],
            "final_steps": [
                {"type": "pgsql", "code": "alter table some add column one int", "position": 1},
            ]
        }), content_type='application/json').data
    assert data['uid'] == "234234234234234"
    assert Case.objects.get(id=33322)


@pytest.mark.parametrize('case__id', [33322])
def test_update_migration(migration_factory, mocked_fogbugz, admin_client, case, case__id):
    """Test update migration."""
    migration = migration_factory(case=case)
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = '1516'
    mocked_case.dtfixfor.string = '2015-01-18T23:00:00Z'
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = 'some-ci-project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": migration.uid,
            "parent": migration.parent,
            "case": {
                "id": case__id
            },
            "category": "onl",
            "pre_deploy_steps": [
                {"type": "mysql", "code": "SELECT * from some", "position": 1},
            ],
            "post_deploy_steps": [
                {"type": "python", "code": "import some", "position": 1},
            ],
            "final_steps": [
                {"type": "pgsql", "code": "alter table some add column one int", "position": 1},
            ]
        }), content_type='application/json').data
    assert data['uid'] == migration.uid


def test_create_instance(admin_client, ci_project):
    """Test create instance."""
    data = admin_client.post(
        '/api/instances/', data=json.dumps({
            "name": "Some instance name",
            "description": "Some instance description",
            "ci_projects": [{
                "name": ci_project.name
            }],
        }), content_type='application/json').data
    assert data['id']


def test_create_instance_no_ci_project(admin_client):
    """Test create instance with wrong CI project passed."""
    data = admin_client.post(
        '/api/instances/', data=json.dumps({
            "name": "Some instance name",
            "description": "Some instance description",
            "ci_projects": [{
                "name": 'not-there'
            }],
        }), content_type='application/json').data
    assert data['id']


def test_create_migration_step_report(mocked_fogbugz, admin_client, instance, case, migration_factory):
    """Test create migration step report."""
    migration = migration_factory(case=case)
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = '1516'
    mocked_case.dtfixfor.string = '2015-01-18T23:00:00Z'
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = instance.ci_projects.first().name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_projects": [{
                        "name": instance.ci_projects.first().name
                    }],
                },
                "migration": {
                    "uid": migration.uid
                },
            },
            "step": {
                "id": migration.pre_deploy_steps.first().id
            },
            "status": "apl",
            "log": "some log"
        }), content_type='application/json').data
    assert data['status'] == "apl"
    assert MigrationReport.objects.get(id=data['id'])


def test_create_migration_step_report_no_migration(mocked_fogbugz, admin_client, instance, migration_factory):
    """Test create migration report when there's no migration."""
    migration = migration_factory()
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = '1516'
    mocked_case.dtfixfor.string = '2015-01-18T23:00:00Z'
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = instance.ci_projects.first().name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_projects": [{
                        "name": instance.ci_projects.first().name
                    }],
                },
                "migration": {
                    "uid": 1231
                },
            },
            "step": {
                "id": migration.pre_deploy_steps.first().id,
            },
            "status": "apl",
            "log": "some log"
        }), content_type='application/json').data
    assert data == {"report": {"migration": ['Migration matching query does not exist.']}}


def test_create_migration_step_report_update(mocked_fogbugz, admin_client, instance, case, migration_report_factory):
    """Test update migration report."""
    migration_report = migration_report_factory(migration__case=case, instance=instance)
    mocked_case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    mocked_case.sfixfor.string = '1516'
    mocked_case.dtfixfor.string = '2015-01-18T23:00:00Z'
    mocked_case.stitle.string = 'Some title'
    mocked_case.soriginaltitle.string = 'Some original title'
    mocked_case.cixproject.string = instance.ci_projects.first().name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_projects": [{
                        "name": instance.ci_projects.first().name
                    }],
                },
                "migration": {
                    "uid": migration_report.migration.uid
                },
            },
            "step": {
                "id": migration_report.migration.pre_deploy_steps.first().id
            },
            "status": "apl",
            "log": "some log"
        }), content_type='application/json').data
    assert data['status'] == "apl"
    assert parse_datetime(data['datetime']) > migration_report.datetime
    assert MigrationReport.objects.get(id=data['id'])


def test_create_deployment_report(mocked_fogbugz, admin_client, instance, release, case):
    """Test create deployment report."""
    data = admin_client.post(
        '/api/deployment-reports/', data=json.dumps({
            "instance": {
                "name": instance.name,
                "ci_projects": [{
                    "name": instance.ci_projects.first().name
                }],
            },
            "status": DeploymentReport.STATUS_DEPLOYED,
            "log": "some log",
            "cases": [{"id": case.id}]
        }), content_type='application/json').data
    assert data['status'] == DeploymentReport.STATUS_DEPLOYED
    report = DeploymentReport.objects.get(id=data['id'])
    report_case, = report.cases.all()
    assert report_case.id == case.id
    assert CaseEdit.objects.filter(case=case).first().type == CaseEdit.TYPE_DEPLOYMENT_REPORT


def test_case_filter_ci_project(admin_client, case_factory):
    """Test case filter when CI project parameter is used."""
    case_factory(ci_project__name='some-other-project')
    case_factory(ci_project__name='some-project')
    data = admin_client.get(
        '/api/cases/', dict(ci_project='some-project')).data
    assert len(data) == 1
    data = admin_client.get(
        '/api/cases/', dict(ci_project='some-other-project')).data
    assert len(data) == 1


def test_case_filter_release(admin_client, case_factory):
    """Test case filter when release parameter is used."""
    case_factory(release__number=20)
    case_factory(release__number=10)
    data = admin_client.get(
        '/api/cases/', dict(release=10)).data
    assert len(data) == 1
    data = admin_client.get(
        '/api/cases/', dict(release=20)).data
    assert len(data) == 1


def test_case_filter_revision(admin_client, case_factory):
    """Test case filter when release parameter is used."""
    case_factory(revision='123')
    case_factory(revision='456')
    data = admin_client.get(
        '/api/cases/', dict(revision='123')).data
    assert len(data) == 1
    data = admin_client.get(
        '/api/cases/', dict(revision='456')).data
    assert len(data) == 1
    assert data[0]['revision'] == '456'


def test_case_filter_deployed_on(admin_client, case_factory, deployment_report_factory, instance):
    """Test case filter when deployed_on parameter is used."""
    case = case_factory(ci_project=instance.ci_projects.first())
    case_factory()
    deployment_report_factory(
        instance=instance, status=DeploymentReport.STATUS_ERROR, cases=[case])
    deployment_report_factory(status=DeploymentReport.STATUS_ERROR, cases=[case])
    data = admin_client.get(
        '/api/cases/', dict(
            deployed_on=instance.name, ci_project=instance.ci_projects.first().name,
            release=case.release.number)).data
    assert len(data) == 0
    deployment_report_factory(
        instance=instance, status=DeploymentReport.STATUS_DEPLOYED, cases=[case])
    data = admin_client.get(
        '/api/cases/', dict(
            deployed_on=instance.name, ci_project=instance.ci_projects.first().name, release=case.release.number)).data
    assert len(data) == 1


def test_case_filter_exclude_deployed_on(
        admin_client, case_factory, deployment_report_factory, instance, instance_factory, release):
    """Test case filter when exclude_deployed_on parameter is used."""
    case = case_factory(ci_project=instance.ci_projects.first(), release=release)
    case_factory()
    # no deployment reports for the case
    data = admin_client.get(
        '/api/cases/', dict(
            exclude_deployed_on=instance.name,
            ci_project=instance.ci_projects.first().name, release=release.number)).data
    assert len(data) == 1
    assert data[0]['id'] == case.id
    # 3 deployment reports, 2 errored, one successful but for other instance
    deployment_report_factory(
        instance=instance, status=DeploymentReport.STATUS_ERROR,
        cases=[case])
    deployment_report_factory(instance=instance, status=DeploymentReport.STATUS_ERROR, cases=[case])
    other_instance = instance_factory(ci_projects=instance.ci_projects.all())
    deployment_report_factory(instance=other_instance, status=DeploymentReport.STATUS_DEPLOYED, cases=[case])
    data = admin_client.get(
        '/api/cases/', dict(
            exclude_deployed_on=instance.name, ci_project=instance.ci_projects.first().name,
            release=release.number)).data
    assert len(data) == 1
    assert data[0]['id'] == case.id
    # 2 deployment reports, one errored, one succeeded
    deployment_report_factory(
        instance=instance, status=DeploymentReport.STATUS_DEPLOYED, cases=[case])
    data = admin_client.get(
        '/api/cases/', dict(
            exclude_deployed_on=instance.name, ci_project=instance.ci_projects.first().name,
            release=release.number)).data
    assert len(data) == 0
