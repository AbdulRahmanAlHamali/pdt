"""Celery tasks."""
from celery.utils.log import get_task_logger

from celery_once import QueueOnce

from django.conf import settings
from django.db import IntegrityError
from django.core.management import call_command

import fogbugz

from pdt.celery import app
from pdt.core.models import (
    Case,
    Release,
)

logger = get_task_logger(__name__)


@app.task(base=QueueOnce, once=dict(keys=('case_id',), graceful=True))
def update_case_from_fogbugz(case_id):
    """Update case info from fogbugz."""
    logger.info("Start updating case %s", case_id)
    try:
        Case.objects.update_from_fogbugz(case_id)
    except IntegrityError:
        # can be the case without CI project assigned
        pass
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
def send_emails():
    """Send queued emails."""
    logger.info("Start sending queued emails")
    call_command('send_queued_mail', interactive=False)
    logger.info("Task finished")
