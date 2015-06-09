"""PDT core migration admin interface."""
from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render

from django_ace import AceWidget

from ..models import (
    Instance,
    Migration,
    MigrationReport,
    MigrationStep,
    PostDeployMigrationStep,
    PreDeployMigrationStep,
)

from .mixins import (
    ACE_WIDGET_PARAMS,
)
from .columns import (
    case_column,
    ci_project_column,
    migration_column,
    release_column,
)


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


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    def applied_on(self):
        """Migration 'applied on' column."""
        return mark_safe(
            '<ul>{0}</ul>'.format("".join('<li><a href="{url}">{name}: {datetime}: {status}</a></li>'.format(
                url=reverse("admin:core_deploymentreport_change", args=(report.id,)),
                name=report.instance.name, datetime=report.datetime, status=report.get_status_display()
            ) for report in self.reports.all())))

    list_display = (
        'id', 'uid', migration_column(lambda obj: obj.parent, order='parent__uid', short_description=_('Parent')),
        case_column(), ci_project_column(lambda obj: obj.case.ci_project, 'case__ci_project__name'),
        release_column(lambda obj: obj.case.release, 'case__release__number'),
        'category', 'reviewed', applied_on)
    list_filter = ('case__id', 'category', 'reviewed')
    search_fields = ('id', 'uid', 'case__id', 'case__title', 'category')
    raw_id_fields = ('case', 'parent')
    autocomplete_lookup_fields = {
        'fk': ['case', 'parent'],
    }
    inlines = [PreDeployMigrationStepInline, PostDeployMigrationStepInline]
    actions = ['mark_migrations_reviewed', 'mark_migrations_not_reviewed', 'stamp_migrations']

    class Media:
        js = ('core/js/admin/migration_inline.js',)

    def save_model(self, request, obj, form, change):
        """Only allow to edit is_reviewed flag."""
        if change:
            obj.refresh_from_db()
            obj.reviewed = form.cleaned_data['reviewed']
        return super(MigrationAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Disable change of related objects."""
        if change:
            for st in formsets:
                st.new_objects = st.changed_objects = st.deleted_objects = []
            return
        return super(MigrationAdmin, self).save_related(request, form, formsets, change)

    def delete_model(self, request, obj):
        """Disable deletion."""
        return

    def get_actions(self, request):
        """Disable delete action."""
        actions = super(MigrationAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def mark_migrations_reviewed(self, request, queryset):
        """Mark migrations reviewed action.

        :param request: django request object
        :param queryset: queryset of the migrations to mark
        """
        queryset.update(reviewed=True)
    mark_migrations_reviewed.short_description = _("Mark selected migrations as reviewed")

    def mark_migrations_not_reviewed(self, request, queryset):
        """Mark migrations as not reviewed action.

        :param request: django request object
        :param queryset: queryset of the migrations to unmark
        """
        queryset.update(reviewed=False)
    mark_migrations_not_reviewed.short_description = _("Mark selected migrations as not reviewed")

    class StampForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        instance = forms.ModelChoiceField(Instance.objects)
        log = forms.CharField(widget=AceWidget(mode="sh", **ACE_WIDGET_PARAMS))

    def stamp_migrations(self, request, queryset):
        """Stamp selected migrations as applied action.

        :param request: django request object
        :param queryset: queryset of the migrations to stamp
        """
        form = None
        form = self.StampForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)},
            data=request.POST or None)

        if 'apply' in request.POST:

            if form.is_valid():
                instance = form.cleaned_data['instance']
                log = form.cleaned_data['log']

                count = 0
                for migration in queryset:
                    report = MigrationReport.objects.get_or_create(migration=migration, instance=instance)[0]
                    report.log = log
                    report.status = MigrationReport.STATUS_APPLIED
                    report.save()
                    count += 1
                self.message_user(request, _("Successfully stamped {count} migration(s).").format(count=count))
                return HttpResponseRedirect(request.get_full_path())

        return render(request, 'admin/core/stamp_migrations.html', {
            'migrations': queryset,
            'form': form,
        })
    stamp_migrations.short_description = _("Stamp selected migrations as applied")

admin.site.register(Migration, MigrationAdmin)
