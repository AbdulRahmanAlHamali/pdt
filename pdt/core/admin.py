"""PDT core admin interface."""
from django.contrib import admin

from .models import (
    Release,
    Instance,
    CIProject,
    Migration,
    MigrationReport,
    Case,
    DeploymentReport,
)


class ReleaseAdmin(admin.ModelAdmin):

    """Release admin interface class."""

admin.site.register(Release, ReleaseAdmin)


class InstanceAdmin(admin.ModelAdmin):

    """Instance admin interface class."""

admin.site.register(Instance, InstanceAdmin)


class CIProjectAdmin(admin.ModelAdmin):

    """CI Project admin interface class."""

admin.site.register(CIProject, CIProjectAdmin)


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

admin.site.register(Migration, MigrationAdmin)


class MigrationReportAdmin(admin.ModelAdmin):

    """MigrationReport admin interface class."""

admin.site.register(MigrationReport, MigrationReportAdmin)


class CaseAdmin(admin.ModelAdmin):

    """Case admin interface class."""

admin.site.register(Case, CaseAdmin)


class DeploymentReportAdmin(admin.ModelAdmin):

    """DeploymentReport admin interface class."""

admin.site.register(DeploymentReport, DeploymentReportAdmin)
