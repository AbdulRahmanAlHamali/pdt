"""PDT core models."""
from django.db import models


class Release(models.Model):

    """Release."""

    name = models.CharField(max_length=255, blank=False, unique=True)
    date = models.DateField(blank=False)

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


class Project(models.Model):

    """Project.

    Continuous integration project.
    """

    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{self.name}'.format(self=self)


class Migration(models.Model):

    """Migration."""

    CATEGORY_CHOICES = (
        ('off', 'Offline'),
        ('onl', 'Online'),
    )

    class Meta:
        unique_together = (('release', 'project'),)

    release = models.ForeignKey(Release, blank=False)
    project = models.ForeignKey(Project, blank=False)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=False, default='onl')
    sql = models.TextField(blank=True)
    code = models.TextField(blank=True)

    def __str__(self):
        return '{self.release}: {self.project}: {self.id}'.format(self=self)


class MigrationReport(models.Model):

    """Migration report."""

    STATUS_CHOICES = (
        ('apl', 'Applied'),
        ('err', 'Error'),
    )

    migration = models.ForeignKey(Migration, blank=False)
    instance = models.ForeignKey(Instance, blank=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return '{self.migration}: {self.instance}: {self.datetime}'.format(self=self)


class Case(models.Model):

    """Bug tracking system case."""

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, blank=False)
    release = models.ForeignKey(Release, blank=False)

    def __str__(self):
        return '{self.id}: {self.title}'.format(self=self)


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
