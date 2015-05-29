"""PDT core models."""
from itertools import chain
import logging

from django.db import transaction
from django.db import models, DatabaseError
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from taggit.managers import TaggableManager

from jsonfield import JSONField

from model_utils import FieldTracker

import fogbugz


logger = logging.getLogger(__name__)


class Release(models.Model):

    """Release."""

    number = models.PositiveIntegerField(blank=False, unique=True, db_index=True)
    datetime = models.DateTimeField(blank=False, default=timezone.now)
    description = models.TextField(blank=True)

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "number__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.number}: {self.datetime:%Y-%m-%d}'.format(self=self)


class CIProject(models.Model):

    """Continuous integration project."""

    name = models.CharField(max_length=255, blank=False, unique=True, db_index=True)
    description = models.TextField(blank=True)

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "name__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.name}'.format(self=self)


class Instance(models.Model):

    """Instance.

    Instance means the isolated set of physical servers.
    """

    name = models.CharField(max_length=255, blank=False, db_index=True)
    ci_project = models.ForeignKey(CIProject, blank=False, related_name="instances")
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (("name", "ci_project"),)
        index_together = (("id", "name"),)

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "name__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.ci_project}: {self.name}'.format(self=self)


class CaseManager(models.Manager):

    """Case manager to allow automatic fetch from Fogbugz."""

    def get_case_info(self, case_id, fb=None):
        """Get case infor from the Fogbugz API.

        :param case_id: Fogbugz case id
        :type case_id: int
        :param fb: optional fogbugz client instance
        """
        if fb is None:
            fb = fogbugz.FogBugz(
                settings.AUTH_FOGBUGZ_SERVER,
                settings.FOGBUGZ_TOKEN)
        resp = fb.search(
            q=case_id,
            cols='sTitle,sOriginalTitle,sFixFor,dtFixFor,sProject,sArea,dtLastUpdated,tags,' +
            settings.FOGBUGZ_CI_PROJECT_FIELD_ID,
            max=1
        )
        case = resp.cases.find('case')
        if case is None:
            raise ValidationError('Case with such id cannot be found', case_id)
        return self.parse_case_info(case)

    def parse_case_info(self, case):
        """Parse case info given the case xml.

        :param case: beautifulsoup object represing the case xml node

        :return: case info dictionary
        :rtype: dict
        """
        case_id = int(case.attrs['ixbug'])
        if not case.sfixfor.string:
            raise ValidationError('Case milestone is not set', case_id)
        ci_project = getattr(case, settings.FOGBUGZ_CI_PROJECT_FIELD_ID).string
        release_datetime = parse_datetime(case.dtfixfor.string) if case.dtfixfor.string else None
        release_number = case.sfixfor.string if case.sfixfor.string.isdigit() else None
        if release_number:
            release, _ = Release.objects.get_or_create(number=release_number)
            if release_datetime and release.datetime != release_datetime:
                release.datetime = release_datetime
                release.save()
        else:
            release = None
        info = dict(
            id=int(case_id),
            release=release,
            project=case.sproject.string,
            area=case.sarea.string,
            title=case.stitle.string,
            description=case.soriginaltitle.string,
            modified_date=parse_datetime(case.dtlastupdated.string) if case.dtlastupdated.string else None,
            tags=frozenset(tag.string.strip() for tag in case.tags.findAll('tag'))
        )
        if ci_project:
            info['ci_project'] = CIProject.objects.get_or_create(name=ci_project)[0]
        return info

    def update_from_fogbugz(self, case_id):
        """Update the case from the Fogbugz API.

        :param id: Fogbugz case id
        """
        case, created = self.get_or_create_from_fogbugz(case_id)
        if not created:
            case_info = self.get_case_info(case_id)
            tags = case_info.pop('tags')
            self.filter(id=case_id).update(**case_info)
            if tags:
                case.tags.set(*set(tags))
                case.save()

    def update_to_fogbugz_migration_url(self, case, fb, case_info, params):
        """Update the case with migration url.

        :param case: case object
        :type case: core.models.Case
        :param fb: fogbugz api client object
        :param case_info: case information dictionary
        :type case_info: dict
        :param params: optional case edit params
        :type params: dict

        :return: fogbugz api response object
        """
        response = fb.edit(
            ixbug=case.id,
            **{settings.FOGBUGZ_MIGRATION_URL_FIELD_ID: 'http://{0}{1}'.format(
                settings.HOST_NAME,
                reverse(
                    'admin:core_migration_change',
                    args=(case.migration.id,)))})
        return response

    def update_to_fogbugz_migration_reviewed(self, case, fb, case_info, params):
        """Update the case when migration is reviewed.

        :param case: case object
        :type case: core.models.Case
        :param fb: fogbugz api client object
        :param case_info: case information dictionary
        :type case_info: dict
        :param params: optional case edit params
        :type params: dict

        :return: fogbugz api response object
        """
        if 'migration-reviewed' not in case_info['tags']:
            response = fb.edit(
                ixbug=case.id,
                sEvent=__('Migration was marked as reviewed'),
                sTags=','.join(case_info['tags'].union({'migration-reviewed'})))
            return response

    def update_to_fogbugz_migration_unreviewed(self, case, fb, case_info, params):
        """Update the case when migration is unreviewed.

        :param case: case object
        :type case: core.models.Case
        :param fb: fogbugz api client object
        :param case_info: case information dictionary
        :type case_info: dict
        :param params: optional case edit params
        :type params: dict

        :return: fogbugz api response object
        """
        if 'migration-reviewed' in case_info['tags']:
            response = fb.edit(
                ixbug=case.id,
                sEvent=__('Migration was unmarked as reviewed'),
                sTags=','.join(case_info['tags'].difference({'migration-reviewed'})))
            return response

    def update_to_fogbugz_migration_report(self, case, fb, case_info, params):
        """Update the case about the migration application.

        :param case: case object
        :type case: core.models.Case
        :param fb: fogbugz api client object
        :param case_info: case information dictionary
        :type case_info: dict
        :param params: optional case edit params
        :type params: dict

        :return: fogbugz api response object
        """
        instance = Instance.objects.get(id=params['instance'])
        messages = {
            MigrationReport.STATUS_APPLIED: __(
                'Migration was applied on {instance} successfully with log:\n{log}'
                '\nSee the detailed migration report here: {report_url}.'),
            MigrationReport.STATUS_ERROR: __(
                'Migration has failed to apply on {instance} with log:\n{log}'
                '\nSee the detailed migration report here: {report_url}.'),
            MigrationReport.STATUS_APPLIED_PARTIALLY: __(
                'Migration was applied partially on {instance} with log:\n{log}'
                '\nSee the detailed migration report here: {report_url}.'),
        }
        report = MigrationReport.objects.get(instance=instance, migration=case.migration)
        kwargs = {}
        if report.status == MigrationReport.STATUS_APPLIED:
            kwargs['sTags'] = ','.join(case_info['tags'].union({'migration-applied-{0}'.format(instance.name)}))
        response = fb.edit(
            ixbug=case.id,
            sEvent=messages[report.status].format(
                instance=instance.name,
                report_url='http://{0}{1}'.format(
                    settings.HOST_NAME,
                    reverse(
                        'admin:core_migrationreport_change',
                        args=(report.id,))),
                log=report.log),
            **kwargs
        )
        return response

    def update_to_fogbugz_deployment_report(self, case, fb, case_info, params):
        """Update the case about the deployment.

        :param case: case object
        :type case: core.models.Case
        :param fb: fogbugz api client object
        :param case_info: case information dictionary
        :type case_info: dict
        :param params: optional case edit params
        :type params: dict

        :return: fogbugz api response object
        """
        report = DeploymentReport.objects.get(id=params['report'])
        messages = {
            DeploymentReport.STATUS_DEPLOYED: __(
                'Deployed on {instance} successfully.\nSee the detailed deployment report here: {report_url}.'),
            DeploymentReport.STATUS_ERROR: __(
                'Deployment has failed on {instance}.\nSee the detailed deployment report here: {report_url}.'),
        }
        kwargs = {}
        if report.status == DeploymentReport.STATUS_DEPLOYED:
            kwargs['sTags'] = ','.join(case_info['tags'].union({'deployed-{0}'.format(report.instance.name)}))
        response = fb.edit(
            ixbug=case.id,
            sEvent=messages[report.status].format(
                instance=report.instance.name,
                report_url='http://{0}{1}'.format(
                    settings.HOST_NAME,
                    reverse(
                        'admin:core_deploymentreport_change',
                        args=(report.id,))),
                log=report.log),
            **kwargs
        )
        return response

    @transaction.atomic
    def update_to_fogbugz(self, case_id):
        """Update the case via the Fogbugz API.

        :param id: Fogbugz case id
        """
        case = self.get(id=case_id)
        fb = fogbugz.FogBugz(
            settings.AUTH_FOGBUGZ_SERVER,
            settings.FOGBUGZ_TOKEN)

        case_info = self.get_case_info(case_id, fb=fb)
        try:
            edits = case.edits.select_for_update()
        except DatabaseError:
            # concurrent update is running
            return
        handlers = {
            CaseEdit.TYPE_MIGRATION_URL: self.update_to_fogbugz_migration_url,
            CaseEdit.TYPE_MIGRATION_REVIEWED: self.update_to_fogbugz_migration_reviewed,
            CaseEdit.TYPE_MIGRATION_UNREVIEWED: self.update_to_fogbugz_migration_unreviewed,
            CaseEdit.TYPE_MIGRATION_REPORT: self.update_to_fogbugz_migration_report,
            CaseEdit.TYPE_DEPLOYMENT_REPORT: self.update_to_fogbugz_deployment_report,
        }
        for edit in edits:
            response = None
            handler = handlers.get(edit.type)
            if handler:
                response = handler(case, fb, case_info, edit.params)
            if response and not response.case:
                raise RuntimeError(response)
            edit.delete()

    def get_or_create_from_fogbugz(self, case_id):
        """Get or create an object from the Fogbugz API.

        :param id: Fogbugz case id
        :type id: int
        """
        try:
            return self.get(id=case_id), False
        except self.model.DoesNotExist:
            case_info = self.get_case_info(case_id)
            tags = case_info.pop('tags')
            case, created = self.get_or_create(**case_info)
            case.tags.set(*set(tags))
            case.save()
            return case, created


class Case(models.Model):

    """Bug tracking system case."""

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=False, db_index=True)
    description = models.TextField(blank=True)
    project = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255, blank=True)
    ci_project = models.ForeignKey(CIProject, blank=False)
    release = models.ForeignKey(Release, blank=True, null=True, related_name='cases')
    modified_date = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

    class Meta:
        index_together = (("ci_project", "release"), ("id", "title"))

    objects = CaseManager()

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__icontains", "title__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.id}: {self.title}'.format(self=self)


class CaseEdit(models.Model):

    """Bug tracking system case edit."""

    case = models.ForeignKey(Case, blank=False, related_name='edits')

    TYPE_MIGRATION_URL = 'migration-url'
    TYPE_MIGRATION_REVIEWED = 'migration-reviewed'
    TYPE_MIGRATION_UNREVIEWED = 'migration-unreviewed'
    TYPE_MIGRATION_REPORT = 'migration-report'
    TYPE_DEPLOYMENT_REPORT = 'deployment-report'

    TYPE_CHOICES = (
        (TYPE_MIGRATION_URL, _('Migration URL')),
        (TYPE_MIGRATION_REVIEWED, _('Migration reviewed')),
        (TYPE_MIGRATION_UNREVIEWED, _('Migration unreviewed')),
        (TYPE_MIGRATION_REPORT, _('Migration report')),
        (TYPE_DEPLOYMENT_REPORT, _('Deployment report')),
    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=False)
    params = JSONField(default=None)


class CaseCategory(models.Model):

    """Case category."""

    class Meta:
        index_together = (("id", "position"),)
        ordering = ['position']
        verbose_name_plural = "Case categories"

    position = models.PositiveSmallIntegerField(db_index=True)
    title = models.CharField(max_length=255, blank=False, db_index=True)
    is_hidden = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    def save(self, *args, **kwargs):
        """Make sure is_default is unique."""
        if self.is_default:
            CaseCategory.objects.filter(
                is_default=True).update(is_default=False)
        super(CaseCategory, self).save(*args, **kwargs)


class Migration(models.Model):

    """Migration."""

    CATEGORY_CHOICES = (
        ('off', 'Offline'),
        ('onl', 'Online'),
    )

    uid = models.CharField(max_length=255, blank=False, unique=True)
    case = models.OneToOneField(Case, blank=False, unique=True)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=False, default='onl', db_index=True)
    reviewed = models.BooleanField(blank=False, default=False, db_index=True)

    tracker = FieldTracker()

    class Meta:
        index_together = (("id", "uid", "case"), ("category", "reviewed"))

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "uid__icontains", "case__id__icontains")

    def __str__(self):
        """String representation."""
        return '{self.case}: {self.category}: {self.uid}'.format(self=self)

    def get_steps(self):
        """Get all migration steps."""
        return chain(self.pre_deploy_steps.all(), self.post_deploy_steps.all())


def migration_changes(sender, instance, **kwargs):
    """Update migration link in the fogbugz case."""
    created = kwargs['created']
    if created:
        CaseEdit.objects.get_or_create(case=instance.case, type=CaseEdit.TYPE_MIGRATION_URL)
    changed = instance.tracker.changed()
    if instance.reviewed and instance.reviewed != changed.get('reviewed', instance.reviewed):
        CaseEdit.objects.get_or_create(case=instance.case, type=CaseEdit.TYPE_MIGRATION_REVIEWED)
    if not instance.reviewed and instance.reviewed != changed.get('reviewed', instance.reviewed):
        CaseEdit.objects.get_or_create(case=instance.case, type=CaseEdit.TYPE_MIGRATION_UNREVIEWED)
    from .tasks import update_case_to_fogbugz
    update_case_to_fogbugz.apply_async(kwargs=dict(case_id=instance.case.id))

post_save.connect(migration_changes, sender=Migration)


class MigrationStep(models.Model):

    """Migration step."""

    class Meta:
        index_together = (("id", "position"),)
        ordering = ['position']

    TYPE_CHOICES = (
        ('mysql', 'MySQL'),
        ('pgsql', 'pgSQL'),
        ('python', 'Python'),
        ('sh', 'Shell'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=False)
    code = models.TextField(blank=False)
    path = models.CharField(max_length=255, blank=True, null=True)
    position = models.PositiveSmallIntegerField(db_index=True)

    def clean(self):
        """Require path for non-sql type."""
        if 'sql' not in self.type and not self.path:
            raise ValidationError('Path is required for non-sql migration step type.')

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "type__icontains")

    def __str__(self):
        """String representation."""
        return 'Migration step {self.id}: {self.type}'.format(self=self)  # pylint: disable=W1306


class PreDeployMigrationStep(MigrationStep):

    """Pre-deploy phase migration step."""

    migration = models.ForeignKey(Migration, blank=False, related_name="pre_deploy_steps")


class PostDeployMigrationStep(MigrationStep):

    """Post-deploy phase migration step."""

    migration = models.ForeignKey(Migration, blank=False, related_name="post_deploy_steps")


class MigrationReport(models.Model):

    """Migration report."""

    STATUS_APPLIED = 'apl'
    STATUS_ERROR = 'err'
    STATUS_APPLIED_PARTIALLY = 'prt'

    STATUS_CHOICES = (
        (STATUS_APPLIED, 'Applied'),
        (STATUS_APPLIED_PARTIALLY, 'Applied partially'),
        (STATUS_ERROR, 'Error'),
    )

    class Meta:
        unique_together = (("migration", "instance"),)
        index_together = (("id", "migration"), ("migration", "instance", "datetime", "id"))
        ordering = ['migration', 'instance', 'datetime', 'id']

    migration = models.ForeignKey(Migration, blank=False, related_name='reports')
    instance = models.ForeignKey(Instance, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    datetime = models.DateTimeField(db_index=True, auto_now=True)
    log = models.TextField(blank=True)

    tracker = FieldTracker()

    def __str__(self):
        """String representation."""
        return '{self.migration}: {self.instance}: {self.datetime}: {status}'.format(
            self=self, status=self.get_status_display())

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "migration__uid__icontains", "migration__case__id__icontains")

    def calculate_status(self):
        """Calculate report status based on step reports."""
        migration_steps = frozenset(step.id for step in self.migration.get_steps())
        apl_report_steps = frozenset(
            report.step.id for report in self.step_reports.all() if report.status == self.STATUS_APPLIED)
        err_report_steps = frozenset(
            report.step.id for report in self.step_reports.all() if report.status != self.STATUS_APPLIED)
        if apl_report_steps == migration_steps:
            self.status = self.STATUS_APPLIED
        elif err_report_steps and apl_report_steps:
            self.status = self.STATUS_APPLIED_PARTIALLY
        else:
            self.status = self.STATUS_ERROR
        self.save()

    def calculate_log(self):
        """Calculate report log based on step reports."""
        self.log = "\n\n".join(report.log for report in self.step_reports.all())
        self.save()


def migration_report_changes(sender, instance, **kwargs):
    """Send case updates about migration application status."""
    changed = instance.tracker.changed()
    if instance.log != changed.get('log', instance.log):
        params = dict(instance=instance.instance.id)
        CaseEdit.objects.get_or_create(
            case=instance.migration.case, type=CaseEdit.TYPE_MIGRATION_REPORT, params=params)
    from .tasks import update_case_to_fogbugz
    update_case_to_fogbugz.apply_async(kwargs=dict(case_id=instance.migration.case.id))


post_save.connect(migration_report_changes, sender=MigrationReport)


class MigrationStepReport(models.Model):

    """Migration step report."""

    STATUS_APPLIED = 'apl'
    STATUS_ERROR = 'err'

    STATUS_CHOICES = (
        (STATUS_APPLIED, 'Applied'),
        (STATUS_ERROR, 'Error'),
    )

    class Meta:
        unique_together = (("report", "step"),)
        index_together = (("report", "step", "status"), ("report", "step", "datetime", "id"))
        ordering = ["report", "step", "datetime", "id"]

    report = models.ForeignKey(MigrationReport, blank=False, related_name='step_reports')
    step = models.ForeignKey(MigrationStep, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False, db_index=True)
    datetime = models.DateTimeField(default=timezone.now, db_index=True)
    log = models.TextField(blank=True)

    def __str__(self):
        """String representation."""
        return '{self.report}: {self.step}: {self.datetime}: {status}'.format(
            self=self, status=self.get_status_display())


def migration_step_report_changes(sender, instance, **kwargs):
    """Calculate migration report status."""
    instance.report.calculate_status()
    instance.report.calculate_log()


post_save.connect(migration_step_report_changes, sender=MigrationStepReport)


class DeploymentReport(models.Model):

    """Deployment report."""

    STATUS_DEPLOYED = 'dpl'
    STATUS_ERROR = 'err'

    STATUS_CHOICES = (
        (STATUS_DEPLOYED, 'Deployed'),
        (STATUS_ERROR, 'Error'),
    )

    class Meta:
        index_together = (("release", "instance", "datetime", "id"),)
        ordering = ['release', 'instance', 'datetime', "id"]

    release = models.ForeignKey(Release, blank=False)
    instance = models.ForeignKey(Instance, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    datetime = models.DateTimeField(default=timezone.now)
    log = models.TextField(blank=True)

    tracker = FieldTracker()

    def __str__(self):
        """String representation."""
        return '{self.release}: {self.instance}: {self.datetime}: {status}'.format(
            self=self, status=self.get_status_display())


def deployment_report_changes(sender, instance, **kwargs):
    """Send case updates about the deployment status."""
    changed = instance.tracker.changed()
    if instance.log != changed.get('log', instance.log):
        from .tasks import update_case_to_fogbugz
        for case in instance.release.cases.all():
            params = dict(report=instance.id)
            CaseEdit.objects.get_or_create(
                case=case, type=CaseEdit.TYPE_DEPLOYMENT_REPORT, params=params)
            update_case_to_fogbugz.apply_async(kwargs=dict(case_id=case.id))


post_save.connect(deployment_report_changes, sender=DeploymentReport)
