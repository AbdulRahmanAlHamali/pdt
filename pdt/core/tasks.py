"""Celery tasks."""
from celery.utils.log import get_task_logger

from celery_once import QueueOnce

from django.conf import settings

import fogbugz

from pdt.celery import app
from pdt.core.models import (
    Case,
    Release,
    CaseEdit,
    DeploymentReport,
    MigrationReport,
)

logger = get_task_logger(__name__)


@app.task(base=QueueOnce, once=dict(keys=('case_id',), graceful=True))
def update_case_from_fogbugz(case_id):
    """Update case info from fogbugz."""
    logger.info("Start updating case %s", case_id)
    Case.objects.update_from_fogbugz(case_id)
    logger.info("Task finished")


@app.task(base=QueueOnce, once=dict(keys=('case_id',), graceful=True))
def update_case_to_fogbugz(case_id):
    """Update case info to fogbugz."""
    logger.info("Start updating case %s", case_id)
    Case.objects.update_to_fogbugz(case_id)
    logger.info("Task finished")


@app.task(base=QueueOnce)
def fetch_cases():
    """Fetch missing and update existing cases from fogbugz for all known releases."""
    logger.info("Start fetching cases")
    fb = fogbugz.FogBugz(
        settings.AUTH_FOGBUGZ_SERVER,
        settings.FOGBUGZ_TOKEN)
    release_query = ' OR '.join('milestone:"{0}"'.format(release.number) for release in Release.objects.all())
    resp = fb.search(
        q='({0}) AND ({ciproject}:"*")'.format(release_query, ciproject=settings.FOGBUGZ_CI_PROJECT_FIELD_ID),
        cols='sTitle,sOriginalTitle,sFixFor,dtFixFor,sProject,sArea,dtLastUpdated,tags,' +
        settings.FOGBUGZ_CI_PROJECT_FIELD_ID
    )
    cases = resp.findAll('case')
    logger.info('Found %s cases to fetch from fogbugz', len(cases))
    for case_xml in cases:
        update_case_from_fogbugz.apply_async(kwargs=dict(case_id=int(case_xml.attrs['ixbug'])))
    logger.info("Task finished")


@app.task(base=QueueOnce, once=dict(graceful=True))
def update_cases_from_fogbugz():
    """Update cases info from fogbugz."""
    logger.info("Start updating cases from fogbugz")
    cases = Case.objects.filter(release__isnull=True)
    logger.info("Found %s cases to update from fogbugz", len(cases))
    for case in cases:
        update_case_from_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")


@app.task(base=QueueOnce, once=dict(graceful=True))
def update_cases_to_fogbugz():
    """Update cases info to fogbugz."""
    logger.info("Start updating cases to fogbugz")
    cases = Case.objects.all()
    logger.info("Found %s cases to update to fogbugz", len(cases))
    for case in cases:
        update_case_to_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")


@app.task(base=QueueOnce, once=dict(graceful=True))
def notify_deployed_cases():
    """Notify previously not notified cases which were deployed."""
    logger.info("Start notifying deployed but not notified cases")
    cases = Case.objects.extra(
        tables=['core_ciproject', 'core_instance', 'core_deploymentreport'],
        where=[
            '"core_case"."ci_project_id"="core_ciproject"."id"',
            '"core_instance"."ci_project_id"="core_ciproject"."id"',
            '"core_deploymentreport"."instance_id"="core_instance"."id"',
            '"core_deploymentreport"."status"=%s',
        ],
        params=[DeploymentReport.STATUS_DEPLOYED]
    ).select_related('ci_project').distinct()
    logger.info("Found %s deployed but not notified cases", len(cases))
    for case in cases:
        schedule_update = False
        tags = set(case.tags.names())
        for instance in case.ci_project.instances.all():
            if 'deployed-{0}'.format(instance.name) not in tags:
                CaseEdit.objects.get_or_create(case=case, type=CaseEdit.TYPE_DEPLOYMENT_REPORT, params=dict(
                    report=instance.deployment_reports.filter(
                        status=DeploymentReport.STATUS_DEPLOYED).order_by('-id')[0].id))
                schedule_update = True
        if schedule_update:
            update_case_to_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")


@app.task(base=QueueOnce, once=dict(graceful=True))
def notify_migrated_cases():
    """Notify previously not notified cases whose migrations were applied."""
    logger.info("Start notifying migrated but not notified cases")
    cases = Case.objects.extra(
        tables=['core_ciproject', 'core_instance', 'core_migrationreport', 'core_migration'],
        where=[
            '"core_case"."ci_project_id"="core_ciproject"."id"',
            '"core_migration"."case_id"="core_case"."id"',
            '"core_instance"."ci_project_id"="core_ciproject"."id"',
            '"core_migrationreport"."migration_id"="core_migration"."id"',
            '"core_migrationreport"."instance_id"="core_instance"."id"',
            '"core_migrationreport"."status"=%s',
        ],
        params=[MigrationReport.STATUS_APPLIED]
    ).select_related('ci_project').distinct()
    logger.info("Found %s migrated but not notified cases", len(cases))
    for case in cases:
        schedule_update = False
        tags = set(case.tags.names())
        for instance in case.ci_project.instances.all():
            if 'migration-applied-{0}'.format(instance.name) not in tags:
                CaseEdit.objects.get_or_create(case=case, type=CaseEdit.TYPE_MIGRATION_REPORT, params=dict(
                    instance=instance.id))
                schedule_update = True
        if schedule_update:
            update_case_to_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")
