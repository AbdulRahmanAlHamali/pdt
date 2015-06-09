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
    release_column,
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
    list_display = ('id', release_column(), instance_column(), 'status', 'datetime')
    list_filter = ('release__number', 'instance__name', 'status')
    search_fields = ('release__number', 'instance__name')
    raw_id_fields = ('release', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['release', 'instance'],
    }


admin.site.register(DeploymentReport, DeploymentReportAdmin)
