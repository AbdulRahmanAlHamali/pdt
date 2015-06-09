"""PDT core case admin interface."""
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from ..models import Case
from ..tasks import update_case_to_fogbugz

from .mixins import (
    TinyMCEMixin
)
from .columns import (
    ci_project_column,
    release_column,
    migration_column,
    tags
)


class CaseAdmin(TinyMCEMixin, admin.ModelAdmin):

    """Case admin interface class."""

    def title(self):
        """Get case title link."""
        return mark_safe(
            '<a href="{url}" target="_blank">{title}</a>'.format(
                url=self.url,
                title=self.title)
        )

    list_display = ('id', title, ci_project_column(), release_column(), migration_column(), 'project', 'area', tags)
    list_filter = ('ci_project__name', 'release', 'project', 'area')
    search_fields = ('id', 'title')
    raw_id_fields = ('ci_project', 'release')
    autocomplete_lookup_fields = {
        'fk': ['ci_project', 'release'],
    }

    def trigger_sync(self, request, queryset):
        """Trigger sync with issue tracking system.

        :param request: django request object
        :param queryset: queryset of the cases to trigger the sync on
        """
        for case in queryset:
            update_case_to_fogbugz.delay(case_id=case.id)
    trigger_sync.short_description = _("Trigger the sync of the selected cases")

    actions = [trigger_sync]

admin.site.register(Case, CaseAdmin)
