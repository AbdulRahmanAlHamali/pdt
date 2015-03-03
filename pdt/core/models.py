"""PDT core models."""
import datetime

from django.db import models
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError

import fogbugz


class Release(models.Model):

    """Release."""

    name = models.CharField(max_length=255, blank=False, unique=True)
    date = models.DateField(blank=False, default=datetime.date.today)

    def __str__(self):
        return '{self.name}: {self.date}'.format(self=self)


class Instance(models.Model):

    """Instance.

    Instance means the isolated set of physical servers.
    """

    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{self.name}'.format(self=self)


class CIProject(models.Model):

    """Continuous integration project."""

    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{self.name}'.format(self=self)


class CaseManager(models.Manager):

    """Case manager to allow automatic fetch from Fogbugz."""

    def get_or_create(self, id=None, **kwargs):
        """Get or create an object from the Fogbugz API.

        :param id: Fogbugz case id
        :type id: int
        """
        try:
            return self.get(id=id, **kwargs), False
        except self.model.DoesNotExist:
            fb = fogbugz.FogBugz(
                settings.AUTH_FOGBUGZ_SERVER,
                settings.FOGBUGZ_TOKEN)
            resp = fb.search(
                q=id,
                cols='sTitle,sOriginalTitle,sFixFor,dtFixFor,sProject,sArea,' + settings.FOGBUGZ_CI_PROJECT_FIELD_ID,
                max=1
            )
            case = resp.cases.find('case')
            kwargs['title'] = case.stitle.string
            kwargs['description'] = case.soriginaltitle.string
            if not case.dtfixfor.string:
                raise ValidationError('Case milestone is not set.')
            kwargs['release'], created = Release.objects.get_or_create(name=case.sfixfor.string)
            kwargs['release'].date = parse_datetime(case.dtfixfor.string)
            kwargs['release'].save()
            ci_project = getattr(case, settings.FOGBUGZ_CI_PROJECT_FIELD_ID).string
            kwargs['ci_project'], created = CIProject.objects.get_or_create(name=ci_project)
            kwargs['project'] = case.sproject.string
            kwargs['area'] = case.sarea.string
            return super(CaseManager, self).get_or_create(id=id, **kwargs)


class Case(models.Model):

    """Bug tracking system case."""

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    project = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255, blank=True)
    ci_project = models.ForeignKey(CIProject, blank=False)
    release = models.ForeignKey(Release, blank=False)

    objects = CaseManager()

    def __str__(self):
        return '{self.id}: {self.title}'.format(self=self)


class Migration(models.Model):

    """Migration."""

    CATEGORY_CHOICES = (
        ('off', 'Offline'),
        ('onl', 'Online'),
    )

    case = models.OneToOneField(Case, blank=False, unique=True)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=False, default='onl')
    sql = models.TextField(blank=True)
    code = models.TextField(blank=True)

    def __str__(self):
        return '{self.case}: {self.category}: {self.id}'.format(self=self)


class MigrationReport(models.Model):

    """Migration report."""

    STATUS_CHOICES = (
        ('apl', 'Applied'),
        ('err', 'Error'),
    )

    class Meta:
        unique_together = (("migration", "instance"),)

    migration = models.ForeignKey(Migration, blank=False)
    instance = models.ForeignKey(Instance, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return '{self.migration}: {self.instance}: {self.datetime}'.format(self=self)


class DeploymentReport(models.Model):

    """Deployment report."""

    STATUS_CHOICES = (
        ('dpl', 'Deployed'),
        ('err', 'Error'),
    )

    release = models.ForeignKey(Release, blank=False)
    instance = models.ForeignKey(Instance, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return '{self.release}: {self.instance}: {self.datetime}'.format(self=self)
