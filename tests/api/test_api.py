"""Test public API."""


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
    json = admin_client.get(
        '/api/migrations/?status=apl').data
    assert len(json) == 1
    assert json[0]['id'] == mr1.id


def test_migration_filter_ci_project(admin_client, migration_report_factory):
    """Test migration filter when ci project parameter is used."""
    migration_report_factory(instance__ci_project__name='some-other-project')
    migration_report_factory(instance__ci_project__name='some-project')
    json = admin_client.get(
        '/api/migrations/?ci_project=some-project').data
    assert len(json) == 1
    json = admin_client.get(
        '/api/migrations/?ci_project=some-other-project').data
    assert len(json) == 1
