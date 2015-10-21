"""PDT core instance admin interface."""
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from ..models import (
    DeploymentReport,
    Instance,
)
from .columns import ci_projects_column


class InstanceAdmin(admin.ModelAdmin):

    """Instance admin interface class."""

    def last_deployed_release(self):
        """Last deployed release column."""
        report = self.deployment_reports.filter(status=DeploymentReport.STATUS_DEPLOYED).order_by('-datetime').first()
        try:
            max_release = max(
                (case.release for case in report.cases.all() if case.release), key=lambda case: case.release.number)
        except (ValueError, AttributeError):
            return ''
        return mark_safe(
            '<a href="{url}">{number}: {datetime}</a>'.format(
                url=reverse("admin:core_release_change", args=(report.id,)),
                number=max_release.number,
                datetime=report.datetime,
            ))

    list_display = ('id', 'name', 'description', ci_projects_column(), last_deployed_release, 'notification_template')
    list_filter = ('ci_projects__name',)
    search_fields = ('id', 'name', 'description')
    raw_id_fields = ('ci_projects', 'notification_template')
    autocomplete_lookup_fields = {
        'm2m': ['ci_projects'],
        'fk': ['notification_template']
    }

admin.site.register(Instance, InstanceAdmin)
