"""Test public API."""


def test_migration_filter_exclude_status(admin_client, migration_report_factory):
    """Test migration filter."""
    migration_report_factory(status='apl')
    json = admin_client.get(
        '/api/migrations/?exclude_status=apl').data
    assert json == []


def test_migration_filter_status(admin_client, migration_report_factory):
    """Test migration filter."""
    migration_report_factory(status='apl')
    json = admin_client.get(
        '/api/migrations/?status=apl').data
    assert len(json) == 1


def test_migration_filter_ci_project(admin_client, migration_report_factory):
    """Test migration filter."""
    migration_report_factory(instance__ci_project__name='some-project')
    json = admin_client.get(
        '/api/migrations/?ci_project=some-project').data
    assert len(json) == 1
