"""PDT core instance admin interface."""
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from ..models import (
    DeploymentReport,
    Instance,
)
from .columns import ci_project_column


class InstanceAdmin(admin.ModelAdmin):

    """Instance admin interface class."""

    def last_deployed_release(self):
        """Last deployed release column."""
        report = self.deployment_reports.filter(status=DeploymentReport.STATUS_DEPLOYED).order_by('-datetime').first()
        return mark_safe(
            '<a href="{url}">{number}: {datetime}</a>'.format(
                url=reverse("admin:core_release_change", args=(report.id,)),
                number=report.release.number,
                datetime=report.datetime,
            )) if report else ''

    list_display = ('id', 'name', 'description', ci_project_column(), last_deployed_release)
    list_filter = ('ci_project__name',)
    search_fields = ('id', 'name', 'description')
    raw_id_fields = ('ci_project',)
    autocomplete_lookup_fields = {
        'fk': ['ci_project'],
    }

admin.site.register(Instance, InstanceAdmin)
