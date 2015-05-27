"""Celery tasks."""
from __future__ import absolute_import

from celery.task.schedules import crontab  # pylint: disable=E0611
from celery.decorators import periodic_task  # pylint: disable=E0611
from celery.utils.log import get_task_logger

from django.conf import settings

import fogbugz

from pdt.celery import app
from pdt.core.models import Case, Release

logger = get_task_logger(__name__)


@app.task
def update_case_from_fogbugz(case_id):
    """Update case info from fogbugz."""
    logger.info("Start updating case %s", case_id)
    Case.objects.update_from_fogbugz(case_id)
    logger.info("Task finished")


@app.task
def update_case_to_fogbugz(case_id):
    """Update case info to fogbugz."""
    logger.info("Start updating case %s", case_id)
    Case.objects.update_to_fogbugz(case_id)
    logger.info("Task finished")


@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def fetch_cases():
    """Fetch missing and update existing cases from fogbugz for all known releases."""
    logger.info("Start fetching cases")
    fb = fogbugz.FogBugz(
        settings.AUTH_FOGBUGZ_SERVER,
        settings.FOGBUGZ_TOKEN)
    release_query = ' OR '.join('milestone: {0}'.format(release.number) for release in Release.objects.all())
    resp = fb.search(
        q=release_query,
        cols='sTitle,sOriginalTitle,sFixFor,dtFixFor,sProject,sArea,dtLastUpdated,tags,' +
        settings.FOGBUGZ_CI_PROJECT_FIELD_ID
    )
    for case_xml in resp.findAll('case'):
        case_id = int(case_xml.attrs['ixbug'])
        logger.debug('Fetched case %s to update', case_id)
        update_case_from_fogbugz.apply_async(kwargs=dict(case_id=case_id))
    logger.info("Task finished")


@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def update_cases():
    """Update cases info from and to fogbugz."""
    logger.info("Start updating cases")
    cases = Case.objects.filter(release__isnull=True)
    logger.info("Found %s cases to update from fogbugz", len(cases))
    for case in cases:
        update_case_from_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    cases = Case.objects.all()
    logger.info("Found %s cases to update to fogbugz", len(cases))
    for case in cases:
        update_case_to_fogbugz.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")
