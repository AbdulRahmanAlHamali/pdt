"""PDT core migration report admin interface."""
from django.contrib import admin
from django import forms

from django_ace import AceWidget

from ..models import (
    MigrationReport,
    MigrationStepReport,
)

from .mixins import (
    ACE_WIDGET_PARAMS,
    LogAdminMixin,
)
from .columns import (
    case_column,
    instance_column,
    migration_column,
    release_column,
)


class MigrationReportForm(forms.ModelForm):

    """Migration report form."""

    class Meta:
        model = MigrationReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class MigrationStepReportForm(forms.ModelForm):

    """Migration step report form."""

    class Meta:
        model = MigrationStepReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class MigrationStepReportInline(LogAdminMixin, admin.StackedInline):

    """Migration step inline."""

    form = MigrationStepReportForm
    model = MigrationStepReport
    extra = 0
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)
    raw_id_fields = ('step',)
    autocomplete_lookup_fields = {
        'fk': ['step'],
    }


class MigrationReportAdmin(LogAdminMixin, admin.ModelAdmin):

    """MigrationReport admin interface class."""

    form = MigrationReportForm
    list_display = (
        'id', migration_column(), case_column(lambda obj: obj.migration.case, 'migration__case__number'),
        release_column(lambda obj: obj.migration.case.release),
        instance_column(), 'status', 'datetime')
    list_filter = ('instance__name', 'status')
    search_fields = ('migration__uid', 'migration__case__id')
    raw_id_fields = ('migration', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['migration', 'instance'],
    }
    # readonly_fields = ('datetime', 'status')
    inlines = [MigrationStepReportInline]


admin.site.register(MigrationReport, MigrationReportAdmin)
