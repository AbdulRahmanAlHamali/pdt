"""PDT core admin interface."""
from django.contrib import admin
from django import forms

from django_ace import AceWidget

from .models import (
    Release,
    Instance,
    CIProject,
    Migration,
    MigrationStep,
    MigrationReport,
    Case,
    DeploymentReport,
)

ACE_WIDGET_PARAMS = dict(showprintmargin=True, width='100%')


class ReleaseAdmin(admin.ModelAdmin):

    """Release admin interface class."""

    list_display = ('name', 'datetime')
    list_filter = ('datetime',)
    search_fields = ('name', 'datetime')

admin.site.register(Release, ReleaseAdmin)


class CIProjectAdmin(admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('name', 'description')
    search_fields = ('name', 'description')


admin.site.register(CIProject, CIProjectAdmin)


def ci_project(self):
    """Get CI project name."""
    return self.ci_project.name
ci_project.admin_order_field = 'ci_project__name'


class InstanceAdmin(admin.ModelAdmin):

    """Instance admin interface class."""

    list_display = ('name', 'description', ci_project)
    list_filter = ('ci_project__name',)
    search_fields = ('name', 'description')
    raw_id_fields = ('ci_project',)
    autocomplete_lookup_fields = {
        'fk': ['ci_project'],
    }

admin.site.register(Instance, InstanceAdmin)


def case(self):
    """Get case id."""
    return self.case.id
case.admin_order_field = 'case__id'


class MigrationStepForm(forms.ModelForm):

    """Migration form."""

    class Meta:
        model = MigrationStep
        fields = '__all__'
        widgets = {
            "code": AceWidget(**ACE_WIDGET_PARAMS),
            "position": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        """Set code widget mode."""
        super(MigrationStepForm, self).__init__(*args, **kwargs)
        type_ = self.initial.get('type')
        if type_:
            self.fields['code'].widget = AceWidget(mode=type_, **ACE_WIDGET_PARAMS)

    def clean_path(self):
        """Optionally make path required."""
        if self.cleaned_data['type'] not in ('sql',) and not self.cleaned_data['path']:
            raise forms.ValidationError('Path is required for non-sql migration step type.')


class MigrationStepInline(admin.StackedInline):

    """Migration step inline."""

    form = MigrationStepForm
    model = MigrationStep
    extra = 0
    sortable_field_name = "position"
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    list_display = (case, 'category')
    list_filter = ('case__id', 'category',)
    search_fields = ('case__id', 'case__title', 'category')
    raw_id_fields = ('case',)
    autocomplete_lookup_fields = {
        'fk': ['case'],
    }
    inlines = [MigrationStepInline]

    class Media:
        js = ('core/js/admin/migration_inline.js',)


admin.site.register(Migration, MigrationAdmin)


def migration_case(self):
    """Get migration case id."""
    return self.migration.case.id
migration_case.admin_order_field = 'migration__case__id'


class MigrationReportForm(forms.ModelForm):

    """Migration report form."""

    class Meta:
        model = MigrationReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class MigrationReportAdmin(admin.ModelAdmin):

    """MigrationReport admin interface class."""

    form = MigrationReportForm
    list_display = (migration_case, 'instance', 'status', 'datetime')
    list_filter = ('instance__name', 'status')
    search_fields = ('migration__uid', 'migration__case__id')
    raw_id_fields = ('migration', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['migration', 'instance'],
    }


admin.site.register(MigrationReport, MigrationReportAdmin)


class CaseAdmin(admin.ModelAdmin):

    """Case admin interface class."""

    list_display = ('id', 'title', 'ci_project', 'release', 'project', 'area')
    list_filter = ('ci_project__name', 'release', 'project', 'area')
    search_fields = ('id', 'title')
    raw_id_fields = ('ci_project', 'release')
    autocomplete_lookup_fields = {
        'fk': ['ci_project', 'release'],
    }


admin.site.register(Case, CaseAdmin)


class DeploymentReportForm(forms.ModelForm):

    """Deployment report form."""

    class Meta:
        model = DeploymentReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class DeploymentReportAdmin(admin.ModelAdmin):

    """DeploymentReport admin interface class."""

    form = DeploymentReportForm
    list_display = ('release', 'instance', 'status', 'datetime')
    list_filter = ('release__name', 'instance__name', 'status')
    search_fields = ('release__name', 'instance__name')
    raw_id_fields = ('release', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['release', 'instance'],
    }


admin.site.register(DeploymentReport, DeploymentReportAdmin)
