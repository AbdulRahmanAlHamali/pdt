"""PDT core release admin interface."""
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from django_object_actions import DjangoObjectActions

from ..models import Release, DeploymentReport


class ReleaseAdmin(DjangoObjectActions, admin.ModelAdmin):

    """Release admin interface class."""

    def deployed_on(self):
        """'Deployed on' column."""
        return mark_safe(
            '<ul>{0}</ul>'.format("".join('<li><a href="{url}">{name}: {datetime}: {status}</a></li>'.format(
                url=urlquote(reverse("admin:core_deploymentreport_change", args=(report.id,))),
                name=escape(report.instance.name),
                datetime=escape(report.datetime), status=escape(report.get_status_display())
            ) for report in DeploymentReport.objects.filter(cases__in=self.cases.all()).distinct())))

    list_display = ('id', 'number', 'datetime', deployed_on)
    list_filter = ('datetime',)
    ordering = ['-number']
    search_fields = ('id', 'number', 'datetime')

    def generate_release_notes(self, request, obj):
        """Redirect to a page with release notes for this release.

        :param request: django request object
        :param obj: Release object to generate release notes for
        """
        return redirect('release-notes', release_number=obj.number)
    generate_release_notes.label = _("Generate release notes")
    generate_release_notes.short_description = _("Redirect to the rendered release notes")

    objectactions = ['generate_release_notes']


admin.site.register(Release, ReleaseAdmin)
