"""Test public API."""
import json

import pytest

from pdt.core.models import Case


def test_migration_filter_exclude_status(admin_client, migration_report_factory, equals_any):
    """Test migration filter when exclude status parameter is used."""
    mr1 = migration_report_factory(status='apl')
    mr2 = migration_report_factory(
        status='err', migration=mr1.migration, instance__ci_project=mr1.instance.ci_project)
    data = admin_client.get(
        '/api/migrations/?exclude_status=apl').data
    assert len(data) == 1
    migration = mr2.migration
    assert data[0] == {
        'id': migration.id,
        'uid': migration.uid,
        'case': {
            'id': migration.case.id,
            'title': migration.case.title,
            'ci_project': migration.case.ci_project.name
        },
        'category': migration.category,
        'sql': migration.sql,
        'code': migration.code,
        'migration_reports': [{
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
        '/api/migrations/?status=apl').data
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
            "sql": "SELECT * from some",
            "code": "import py"
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
            "sql": "SELECT * from some",
            "code": "import py"
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
            "sql": "SELECT * from some",
            "code": "import py"
        }), content_type='application/json').data
    assert data['uid'] == "234234234234234"
    assert Case.objects.get(id=33322)


@pytest.mark.parametrize('case__id', [33322])
def test_update_migration(migration_factory, mocked_fogbugz, admin_client, migration, case__id):
    """Test update migration."""
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
            "uid": "234234234234234",
            "case": {
                "id": case__id
            },
            "category": "onl",
            "sql": "SELECT * from some",
            "code": "import py"
        }), content_type='application/json').data
    assert data['uid'] == "234234234234234"
