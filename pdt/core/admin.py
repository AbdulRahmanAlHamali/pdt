"""PDT core admin interface."""
from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from django_ace import AceWidget

from .models import (
    Release,
    Instance,
    CIProject,
    Migration,
    MigrationStep,
    PreDeployMigrationStep,
    PostDeployMigrationStep,
    MigrationReport,
    MigrationStepReport,
    Case,
    DeploymentReport,
)

ACE_WIDGET_PARAMS = dict(showprintmargin=False, width='100%')


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
        abstract = True
        fields = '__all__'
        widgets = {
            "code": AceWidget(**ACE_WIDGET_PARAMS),
            "position": forms.HiddenInput,
        }

    class Media:
        js = ['django_ace/ace/mode-{0}.js'.format(mode) for mode, _ in MigrationStep.TYPE_CHOICES]

    def __init__(self, *args, **kwargs):
        """Set code widget mode."""
        super(MigrationStepForm, self).__init__(*args, **kwargs)
        type_ = self.initial.get('type')
        if type_:
            self.fields['code'].widget = AceWidget(mode=type_, **ACE_WIDGET_PARAMS)
        widget = self.fields['code'].widget
        widget.__dict__['media'] = widget.media
        self.fields['type'].widget.attrs = {'class': 'migration_step_type'}


class PreDeployMigrationStepForm(MigrationStepForm):

    """Pre-deploy phase migration step form."""

    class Meta(MigrationStepForm.Meta):
        model = PreDeployMigrationStep


class PostDeployMigrationStepForm(MigrationStepForm):

    """Post-deploy phase migration step form."""

    class Meta(MigrationStepForm.Meta):
        model = PostDeployMigrationStep


class PreDeployMigrationStepInline(admin.StackedInline):

    """Pre-deploy migration step inline."""

    form = PreDeployMigrationStepForm
    model = PreDeployMigrationStep
    extra = 0
    sortable_field_name = "position"
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


class PostDeployMigrationStepInline(admin.StackedInline):

    """Post-deploy migration step inline."""

    form = PostDeployMigrationStepForm
    model = PostDeployMigrationStep
    extra = 0
    sortable_field_name = "position"
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


class MigrationStepAdmin(admin.ModelAdmin):

    """MigrationStep admin interface class."""

    list_display = ('id', 'type')
    list_filter = ('type',)
    search_fields = ('type', 'script')
    autocomplete_lookup_fields = {
        'fk': ['migration'],
    }

admin.site.register(MigrationStep, MigrationStepAdmin)


def mark_migrations_reviewed(modeladmin, request, queryset):
    """Mark migrations reviewed."""
    queryset.update(reviewed=True)
mark_migrations_reviewed.short_description = "Mark selected migrations as reviewed"


def mark_migrations_not_reviewed(modeladmin, request, queryset):
    """Mark migrations as not reviewed."""
    queryset.update(reviewed=False)
mark_migrations_not_reviewed.short_description = "Mark selected migrations as not reviewed"


def applied_on(migration):
    """Migration applied on."""
    return mark_safe(", ".join('<a href="{url}">{name}: {datetime}: {status}</a>'.format(
        url=reverse("admin:core_migrationreport_change", args=(report.id,)),
        name=report.instance.name, datetime=report.datetime, status=report.get_status_display())
        for report in migration.reports.all()))
applied_on.short_description = "Applied on"


def case_ci_project(self):
    """Get case ci project."""
    return self.case.ci_project.name
case_ci_project.admin_order_field = 'case__ci_project__name'


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    list_display = (case, case_ci_project, 'category', 'reviewed', applied_on)
    list_filter = ('case__id', 'category', 'reviewed')
    search_fields = ('case__id', 'case__title', 'category')
    raw_id_fields = ('case',)
    autocomplete_lookup_fields = {
        'fk': ['case'],
    }
    inlines = [PreDeployMigrationStepInline, PostDeployMigrationStepInline]
    actions = [mark_migrations_reviewed, mark_migrations_not_reviewed]

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


class MigrationStepReportForm(forms.ModelForm):

    """Migration step report form."""

    class Meta:
        model = MigrationStepReport
        fields = '__all__'
        widgets = {
            "log": AceWidget(mode="sh", **ACE_WIDGET_PARAMS),
        }


class MigrationStepReportInline(admin.StackedInline):

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
    readonly_fields = ('datetime', 'status')
    inlines = [MigrationStepReportInline]


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
