"""Test public API."""
import json

from django.utils.dateparse import parse_datetime
import pytest

from pdt.core.models import Case, MigrationReport, DeploymentReport


def test_migration_filter_exclude_status(admin_client, migration_report_factory, equals_any):
    """Test migration filter when exclude status parameter is used."""
    mr1 = migration_report_factory(status='apl')
    mr2 = migration_report_factory(
        status='err', migration=mr1.migration, instance__ci_project=mr1.instance.ci_project)
    data = admin_client.get(
        '/api/migrations/', exclude_status='apl', ci_project=mr1.instance.ci_project.name).data
    assert len(data) == 1
    migration = mr2.migration
    assert data[0] == {
        'id': migration.id,
        'uid': migration.uid,
        'case': {
            'id': migration.case.id,
            'title': migration.case.title,
            'description': migration.case.description,
            'ci_project': migration.case.ci_project.name
        },
        'pre_deploy_steps': [
            {'id': step.id, 'type': step.type, 'position': step.position, 'code': step.code, 'path': None}
            for step in migration.pre_deploy_steps.all()],
        'post_deploy_steps': [
            {'id': step.id, 'type': step.type, 'position': step.position, 'code': step.code, 'path': None}
            for step in migration.post_deploy_steps.all()],
        'category': migration.category,
        'reviewed': False,
        'reports': [{
            'id': mr1.id,
            'ci_project': migration.case.ci_project.name,
            'instance': mr1.instance.name,
            'status': mr1.status,
            'datetime': equals_any,
            'log': mr1.log
        }, {
            'id': mr2.id,
            'ci_project': migration.case.ci_project.name,
            'instance': mr2.instance.name,
            'status': mr2.status,
            'datetime': equals_any,
            'log': mr2.log
        }]
    }


def test_migration_filter_status(admin_client, migration_report_factory):
    """Test migration filter when status parameter is used."""
    mr1 = migration_report_factory(status='apl')
    migration_report_factory(
        status='err', migration=mr1.migration, instance__ci_project=mr1.instance.ci_project)
    data = admin_client.get(
        '/api/migrations/', status='apl', ci_project=mr1.instance.ci_project.name).data
    assert len(data) == 1
    assert data[0]['id'] == mr1.id


def test_migration_filter_ci_project(admin_client, migration_factory):
    """Test migration filter when ci project parameter is used."""
    migration_factory(case__ci_project__name='some-other-project')
    migration_factory(case__ci_project__name='some-project')
    data = admin_client.get(
        '/api/migrations/?ci_project=some-project').data
    assert len(data) == 1
    data = admin_client.get(
        '/api/migrations/?ci_project=some-other-project').data
    assert len(data) == 1


def test_migration_filter_reviewed(admin_client, migration_factory):
    """Test migration filter when reviewed parameter is used."""
    migration1 = migration_factory(reviewed=False)
    migration2 = migration_factory(reviewed=True)
    data = admin_client.get(
        '/api/migrations/?reviewed=True').data
    assert len(data) == 1
    assert data[0]['uid'] == migration2.uid
    data = admin_client.get(
        '/api/migrations/?reviewed=False').data
    assert len(data) == 1
    assert data[0]['uid'] == migration1.uid


def test_create_migration_no_case(mocked_fogbugz, admin_client):
    """Test create migration when fb case is not found."""
    mocked_fogbugz.return_value.search.return_value.cases.find.return_value = None
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [],
            "post_deploy_steps": []
        }), content_type='application/json').data
    assert data == {'case': ["['Case with such id cannot be found']"]}


def test_create_migration_case_no_milestone(mocked_fogbugz, admin_client):
    """Test create migration when fb case doesn't have a milestone."""
    mocked_fogbugz.return_value.search.return_value.cases.find.return_value.sfixfor.string = None
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [],
            "post_deploy_steps": []
        }), content_type='application/json').data
    assert data == {'case': ["['Case milestone is not set']"]}


def test_create_migration(mocked_fogbugz, admin_client):
    """Test create migration."""
    case = mocked_fogbugz.return_value.search.return_value.cases.find.return_value
    case.sfixfor.string = '1516'
    case.dtfixfor.string = '2015-01-18T23:00:00Z'
    case.stitle.string = 'Some title'
    case.soriginaltitle.string = 'Some original title'
    case.cixproject.string = 'some-ci-project'
    case.sproject.string = 'Some project'
    case.sproject.string = 'Some project'
    case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migrations/', data=json.dumps({
            "uid": "234234234234234",
            "case": {
                "id": "33322"
            },
            "category": "onl",
            "pre_deploy_steps": [
                {"type": "mysql", "code": "SELECT * from some", "position": 1},
            ],
            "post_deploy_steps": [
                {"type": "python", "code": "import some", "position": 1},
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
            "case": {
                "id": case__id
            },
            "category": "onl",
            "pre_deploy_steps": [
                {"type": "mysql", "code": "SELECT * from some", "position": 1},
            ],
            "post_deploy_steps": [
                {"type": "python", "code": "import some", "position": 1},
            ]
        }), content_type='application/json').data
    assert data['uid'] == migration.uid


def test_create_instance(admin_client, ci_project):
    """Test create instance."""
    data = admin_client.post(
        '/api/instances/', data=json.dumps({
            "name": "Some instance name",
            "description": "Some instance description",
            "ci_project": {
                "name": ci_project.name
            }
        }), content_type='application/json').data
    assert data['id']


def test_create_instance_no_ci_project(admin_client):
    """Test create instance with wrong ci project passed."""
    data = admin_client.post(
        '/api/instances/', data=json.dumps({
            "name": "Some instance name",
            "description": "Some instance description",
            "ci_project": {
                "name": 'not-there'
            }
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
    mocked_case.cixproject.string = instance.ci_project.name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_project": {
                        "name": instance.ci_project.name
                    },
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
    mocked_case.cixproject.string = instance.ci_project.name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_project": {
                        "name": instance.ci_project.name
                    },
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
    mocked_case.cixproject.string = instance.ci_project.name
    mocked_case.sproject.string = 'Some project'
    mocked_case.sproject.string = 'Some project'
    mocked_case.sarea.string = 'Some area'
    data = admin_client.post(
        '/api/migration-step-reports/', data=json.dumps({
            "report": {
                "instance": {
                    "name": instance.name,
                    "ci_project": {
                        "name": instance.ci_project.name
                    },
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


def test_create_deployment_report(mocked_fogbugz, admin_client, instance, release):
    """Test create deployment report."""
    data = admin_client.post(
        '/api/deployment-reports/', data=json.dumps({
            "instance": {
                "name": instance.name,
                "ci_project": {
                    "name": instance.ci_project.name
                },
            },
            "release": {
                "name": release.name
            },
            "status": "dpl",
            "log": "some log"
        }), content_type='application/json').data
    assert data['status'] == "dpl"
    assert DeploymentReport.objects.get(id=data['id'])
