"""Celery tasks."""
from __future__ import absolute_import

from celery.task.schedules import crontab  # pylint: disable=E0611
from celery.decorators import periodic_task  # pylint: disable=E0611
from celery.utils.log import get_task_logger

from pdt.celery import app
from pdt.core.models import Case

logger = get_task_logger(__name__)


@app.task
def update_case(case_id):
    """Update case info from fogbugz."""
    logger.info("Start updating case %s", case_id)
    Case.objects.update_from_fogbugz(case_id)
    logger.info("Task finished")


@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def update_cases():
    """Update cases info from fogbugz."""
    logger.info("Start updating cases")
    cases = Case.objects.all()
    logger.info("Found %s cases to update", len(cases))
    for case in cases:
        update_case.apply_async(kwargs=dict(case_id=case.id))
    logger.info("Task finished")
