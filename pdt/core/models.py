"""PDT core models."""
from django.db import models
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

import fogbugz


class Release(models.Model):

    """Release."""

    name = models.CharField(max_length=255, blank=False, unique=True)
    datetime = models.DateTimeField(blank=False, default=timezone.now)

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "name__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.name}: {self.datetime:%Y-%m-%d}'.format(self=self)


class CIProject(models.Model):

    """Continuous integration project."""

    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=True)

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

    name = models.CharField(max_length=255, blank=False)
    ci_project = models.ForeignKey(CIProject, blank=False)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = (("name", "ci_project"),)

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "name__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.name}: {self.ci_project}'.format(self=self)


class CaseManager(models.Manager):

    """Case manager to allow automatic fetch from Fogbugz."""

    def get_or_create_from_fogbugz(self, case_id=None, **kwargs):
        """Get or create an object from the Fogbugz API.

        :param id: Fogbugz case id
        :type id: int
        """
        try:
            return self.get(id=case_id, **kwargs), False
        except self.model.DoesNotExist:
            fb = fogbugz.FogBugz(
                settings.AUTH_FOGBUGZ_SERVER,
                settings.FOGBUGZ_TOKEN)
            resp = fb.search(
                q=case_id,
                cols='sTitle,sOriginalTitle,sFixFor,dtFixFor,sProject,sArea,' + settings.FOGBUGZ_CI_PROJECT_FIELD_ID,
                max=1
            )
            case = resp.cases.find('case')
            if case is None:
                raise ValidationError('Case with such id cannot be found', case_id)
            if not case.sfixfor.string:
                raise ValidationError('Case milestone is not set', case_id)
            kwargs['title'] = case.stitle.string
            kwargs['description'] = case.soriginaltitle.string
            release_datetime = parse_datetime(case.dtfixfor.string)
            try:
                release = Release.objects.get(name=case.sfixfor.string)
            except Release.DoesNotExist:
                release = Release(name=case.sfixfor.string, datetime=release_datetime)
            else:
                release.datetime = release_datetime
            release.save()
            kwargs['release'] = release
            ci_project = getattr(case, settings.FOGBUGZ_CI_PROJECT_FIELD_ID).string
            kwargs['ci_project'], _ = CIProject.objects.get_or_create(name=ci_project)
            kwargs['project'] = case.sproject.string
            kwargs['area'] = case.sarea.string
            return super(CaseManager, self).get_or_create(id=case_id, **kwargs)


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

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__icontains", "title__icontains",)

    def __str__(self):
        """String representation."""
        return '{self.id}: {self.title}'.format(self=self)


class Migration(models.Model):

    """Migration."""

    CATEGORY_CHOICES = (
        ('off', 'Offline'),
        ('onl', 'Online'),
    )

    uid = models.CharField(max_length=255, blank=False, unique=True)
    case = models.OneToOneField(Case, blank=False, unique=True)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=False, default='onl')

    @staticmethod
    def autocomplete_search_fields():
        """Auto complete search fields."""
        return ("id__iexact", "uid__icontains", "case__id__icontains")

    def __str__(self):
        """String representation."""
        return '{self.case}: {self.category}: {self.uid}'.format(self=self)


class MigrationStep(models.Model):

    """Migration step."""

    migration = models.ForeignKey(Migration, blank=False)

    TYPE_CHOICES = (
        ('sql', 'SQL'),
        ('python', 'Python'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=False)
    code = models.TextField(blank=False)
    path = models.CharField(max_length=255, blank=True, null=True)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['position']

    # def clean(self):
    #     """Require path for non-sql type."""
    #     if self.type not in ('sql',) and not self.path:
    #         raise ValidationError('Path is required for non-sql migration step type.')


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
    datetime = models.DateTimeField(default=timezone.now)
    log = models.TextField(blank=True)

    def __str__(self):
        """String representation."""
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
    datetime = models.DateTimeField(default=timezone.now)
    log = models.TextField(blank=True)

    def __str__(self):
        """String representation."""
        return '{self.release}: {self.instance}: {self.datetime}'.format(self=self)
