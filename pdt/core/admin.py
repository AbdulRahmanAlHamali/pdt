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

    list_display = ('name', 'date')
    list_filter = ('date',)
    search_fields = ('name', 'date')

admin.site.register(Release, ReleaseAdmin)


class CIProjectAdmin(admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('name', 'description')
    search_fields = ('name', 'description')


admin.site.register(CIProject, CIProjectAdmin)


def ci_project(self):
    return self.ci_project.name
ci_project.admin_order_field = 'ci_project__name'


class InstanceAdmin(admin.ModelAdmin):

    """Instance admin interface class."""

    list_display = (ci_project, 'name', 'description')
    list_filter = ('ci_project__name',)
    search_fields = ('name', 'description')

admin.site.register(Instance, InstanceAdmin)


def case(self):
    return self.case.id
case.admin_order_field = 'case__id'


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    list_display = (case, 'category')
    list_filter = ('case__id', 'category',)
    search_fields = ('case__id', 'case__title', 'category')


admin.site.register(Migration, MigrationAdmin)


def case(self):
    return self.migration.case.id
case.admin_order_field = 'migration__case__id'


class MigrationReportAdmin(admin.ModelAdmin):

    """MigrationReport admin interface class."""

    list_display = ('instance', case, 'status', 'datetime')
    list_filter = ('migration__case__id', 'instance__name', 'status')
    search_fields = ('migration',)


admin.site.register(MigrationReport, MigrationReportAdmin)


class CaseAdmin(admin.ModelAdmin):

    """Case admin interface class."""

    list_display = ('id', 'title', 'ci_project', 'project', 'area')
    list_filter = ('ci_project__name', 'project', 'area')
    search_fields = ('id', 'title')

admin.site.register(Case, CaseAdmin)


def case(self):
    return self.migration.case.id
case.admin_order_field = 'migration__case__id'


class DeploymentReportAdmin(admin.ModelAdmin):

    """DeploymentReport admin interface class."""

    list_display = ('release', 'instance', 'status', 'datetime')
    list_filter = ('release__name', 'instance__name', 'status')
    search_fields = ('release__name', 'instance__name')


admin.site.register(DeploymentReport, DeploymentReportAdmin)
