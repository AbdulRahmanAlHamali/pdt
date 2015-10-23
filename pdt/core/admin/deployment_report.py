"""PDT core deployment report admin interface."""
from django.contrib import admin
from django import forms

from django_ace import AceWidget

from ..models import DeploymentReport

from .mixins import (
    LogAdminMixin,
    ACE_WIDGET_PARAMS
)
from .columns import (
    instance_column,
    cases_column,
)


class DeploymentReportForm(forms.ModelForm):

    """Deployment report form."""

    class Meta:
        model = DeploymentReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class DeploymentReportAdmin(LogAdminMixin, admin.ModelAdmin):

    """DeploymentReport admin interface class."""

    form = DeploymentReportForm
    list_display = ('id', instance_column(), 'status', 'datetime', cases_column())
    list_filter = ('cases__release__number', 'instance__name', 'status')
    search_fields = ('instance__name',)
    raw_id_fields = ('instance', 'cases')
    autocomplete_lookup_fields = {
        'fk': ['instance'],
        'm2m': ['cases'],
    }

    def get_queryset(self, request):
        """Optimize the number of queries made."""
        qs = super(DeploymentReportAdmin, self).get_queryset(request)
        return qs.select_related('instance').prefetch_related('cases')


admin.site.register(DeploymentReport, DeploymentReportAdmin)
