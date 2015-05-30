"""PDT core admin interface."""
import collections
import logging
import pprint

from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, get_object_or_404, render

from constance import config

from django_ace import AceWidget
from django_object_actions import DjangoObjectActions

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
    CaseEdit,
    CaseCategory,
    DeploymentReport,
)

ACE_WIDGET_PARAMS = dict(showprintmargin=False, width='100%')

logger = logging.getLogger(__name__)


class TinyMCEMixin(object):

    """Mixin to add tinymce editor."""

    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/grappelli/tinymce_setup/tinymce_setup.js',
        ]


class ReleaseAdmin(TinyMCEMixin, DjangoObjectActions, admin.ModelAdmin):

    """Release admin interface class."""

    def deployed_on(self):
        """Deployed on."""
        return mark_safe(
            '<ul>{0}</ul>'.format("".join('<li><a href="{url}">{name}: {datetime}: {status}</a></li>'.format(
                url=reverse("admin:core_deploymentreport_change", args=(report.id,)),
                name=report.instance.name, datetime=report.datetime, status=report.get_status_display()
            ) for report in self.deployment_reports.all())))

    list_display = ('id', 'number', 'datetime', deployed_on)
    list_filter = ('datetime',)
    search_fields = ('id', 'number', 'datetime')

    def generate_release_notes(self, request, obj):
        """Redirect to a page with release notes for this release."""
        return redirect('release-notes', release_number=obj.number)
    generate_release_notes.label = _("Generate release notes")
    generate_release_notes.short_description = _("Redirect to the rendered release notes")

    objectactions = ['generate_release_notes']


admin.site.register(Release, ReleaseAdmin)


def release_column(getter=lambda obj: obj.release):
    """Return release column function."""
    def release(self):
        """Get release name."""
        release = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_release_change", args=(release.id,)),
                name=release)) if release else _('n/a')
    release.admin_order_field = 'release__name'
    return release


def normalize_case_title(case_title):
    """Normalize case title."""
    # I'm sick of people adding redundant whitespace to case titles :-)
    case_title = ' '.join(case_title.split())
    # I'm sick of people ending case titles with a dot :-)
    case_title = case_title.rstrip('.')
    return case_title


def find_case_category(case, case_categories):
    """Find case category."""
    default_category = None
    for category in case_categories:
        if set(case['tags']).intersection(frozenset(category['tags'])):
            return category['key']
        if category['default']:
            default_category = category
    return default_category['key'] if default_category else None


def get_release_notes(request, release):
    """Get release notes as a string for given release."""
    cases = []
    unmerged_tags = frozenset(tag.strip() for tag in config.TAGS_FOR_UNMERGED_CASES.split(','))
    # Post-process case titles and tags.
    for case_object in release.cases.all():
        case = dict(tags=frozenset(case_object.tags.names()), id=case_object.id)
        # Normalize case titles.
        case['title'] = normalize_case_title(case_object.title)
        if unmerged_tags.intersection(frozenset(case['tags'])):
            case['unmerged'] = True
        # Remove duplicate tags and provide stable sorting.
        case['tags'] = sorted(set(case['tags']))
        cases.append(case)
    # Build up a mapping of (category => [case, ...]) pairs.
    categorized_cases = collections.defaultdict(list)
    case_categories = [
        dict(
            key=category.id,
            hidden=category.is_hidden,
            title=category.title,
            default=category.is_default,
            tags=category.tags.names(),
        ) for category in CaseCategory.objects.all()]
    for case in cases:
        key = find_case_category(case, case_categories)
        categorized_cases[key].append(case)
    logger.debug("Categorized cases:\n%s", pprint.pformat(dict(categorized_cases)))
    categories = []
    for category in case_categories:
        if category['key'] in categorized_cases and not category['hidden']:
            category['cases'] = [case for case in sorted(categorized_cases[category['key']], key=lambda c: c['id'])]
        categories.append(category)

    return render_to_string('admin/core/release_notes.html', dict(
        release=release, categorized_cases=categorized_cases, categories=categories), RequestContext(request))


def release_notes(request, release_number, **kwargs):
    """Release notes view."""
    release = get_object_or_404(Release.objects.filter(number=release_number))
    return HttpResponse(get_release_notes(request, release))


def release_notes_overview(request):
    """Release notes overview view."""
    notes = []
    for release in Release.objects.all().order_by('-number'):
        notes.append(get_release_notes(request, release))
    return render(
        request, 'admin/core/release_notes_overview.html', dict(
            categories=CaseCategory.objects.filter(is_default=False, is_hidden=False),
            notes=notes))


class CIProjectAdmin(TinyMCEMixin, admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name', 'description')


admin.site.register(CIProject, CIProjectAdmin)


def ci_project_column(getter=lambda obj: obj.ci_project, order='ci_project__name'):
    """Get ci project column function."""
    def ci_project(self):
        ci_project = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_ciproject_change", args=(ci_project.id,)),
                name=ci_project.name))
    ci_project.admin_order_field = order
    return ci_project


class InstanceAdmin(TinyMCEMixin, admin.ModelAdmin):

    """Instance admin interface class."""

    list_display = ('id', 'name', 'description', ci_project_column())
    list_filter = ('ci_project__name',)
    search_fields = ('id', 'name', 'description')
    raw_id_fields = ('ci_project',)
    autocomplete_lookup_fields = {
        'fk': ['ci_project'],
    }

admin.site.register(Instance, InstanceAdmin)


def instance(self):
    """Get instance link column."""
    return mark_safe(
        '<a href="{url}">{name}</a>'.format(
            url=reverse("admin:core_instance_change", args=(self.instance.id,)),
            name=self.instance))
instance.admin_order_field = 'instance__name'


def tags(obj):
    """Tags."""
    return ', '.join(tag.name for tag in obj.tags.all())


class CaseAdmin(TinyMCEMixin, admin.ModelAdmin):

    """Case admin interface class."""

    def title(self):
        """Get case title link."""
        return mark_safe(
            '<a href="{url}" target="_blank">{title}</a>'.format(
                url=self.url,
                title=self.title)
        )

    list_display = ('id', title, ci_project_column(), release_column(), 'project', 'area', tags)
    list_filter = ('ci_project__name', 'release', 'project', 'area')
    search_fields = ('id', 'title')
    raw_id_fields = ('ci_project', 'release')
    autocomplete_lookup_fields = {
        'fk': ['ci_project', 'release'],
    }


admin.site.register(Case, CaseAdmin)


def case_column(getter=lambda obj: obj.case, order='case__id'):
    """Get case column function."""
    def case(self):
        """Get case link."""
        case = getter(self)
        return mark_safe(
            '<a href="{local_url}">{id}</a>: <a href="{external_url}" target="_blank">{title}</a>'.format(
                external_url=case.url,
                local_url=reverse("admin:core_case_change", args=(case.id,)),
                id=case.id,
                title=case.title)
        )
    case.admin_order_field = order
    return case


class CaseEditAdmin(admin.ModelAdmin):

    """Case edit admin interface class."""

    list_display = ('id', case_column(), 'type', 'params')
    list_filter = ('case__id', 'type')
    raw_id_fields = ('case',)
    autocomplete_lookup_fields = {
        'fk': ['case'],
    }


admin.site.register(CaseEdit, CaseEditAdmin)


class CaseCategoryAdmin(admin.ModelAdmin):

    """Case category admin interface class."""

    list_display = ('id', 'position', 'title', tags, 'is_hidden', 'is_default')
    sortable_field_name = "position"


admin.site.register(CaseCategory, CaseCategoryAdmin)


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


def mark_migrations_reviewed(modeladmin, request, queryset):
    """Mark migrations reviewed."""
    queryset.update(reviewed=True)
mark_migrations_reviewed.short_description = _("Mark selected migrations as reviewed")


def mark_migrations_not_reviewed(modeladmin, request, queryset):
    """Mark migrations as not reviewed."""
    queryset.update(reviewed=False)
mark_migrations_not_reviewed.short_description = _("Mark selected migrations as not reviewed")


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    def applied_on(self):
        """Migration applied on."""
        return mark_safe(
            '<ul>{0}</ul>'.format("".join('<li><a href="{url}">{name}: {datetime}: {status}</a></li>'.format(
                url=reverse("admin:core_deploymentreport_change", args=(report.id,)),
                name=report.instance.name, datetime=report.datetime, status=report.get_status_display()
            ) for report in self.reports.all())))

    list_display = (
        'id', 'uid', case_column(), ci_project_column(lambda obj: obj.case.ci_project, 'case__ci_project__name'),
        'category', 'reviewed', applied_on)
    list_filter = ('case__id', 'category', 'reviewed')
    search_fields = ('id', 'uid', 'case__id', 'case__title', 'category')
    raw_id_fields = ('case',)
    autocomplete_lookup_fields = {
        'fk': ['case'],
    }
    inlines = [PreDeployMigrationStepInline, PostDeployMigrationStepInline]
    actions = [mark_migrations_reviewed, mark_migrations_not_reviewed]

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


admin.site.register(Migration, MigrationAdmin)


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

    def migration(self):
        """Migration applied on."""
        return mark_safe('<a href="{url}">{uid}</a>'.format(
            url=reverse("admin:core_migration_change", args=(self.migration.id,)),
            uid=self.migration.uid))
    migration.admin_order_field = 'migration__uid'

    form = MigrationReportForm
    list_display = (
        'id', migration, case_column(lambda obj: obj.migration.case, 'migration__case__number'),
        release_column(lambda obj: obj.migration.case.release),
        instance, 'status', 'datetime')
    list_filter = ('instance__name', 'status')
    search_fields = ('migration__uid', 'migration__case__id')
    raw_id_fields = ('migration', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['migration', 'instance'],
    }
    # readonly_fields = ('datetime', 'status')
    inlines = [MigrationStepReportInline]


admin.site.register(MigrationReport, MigrationReportAdmin)


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
    list_display = ('id', release_column(), instance, 'status', 'datetime')
    list_filter = ('release__number', 'instance__name', 'status')
    search_fields = ('release__number', 'instance__name')
    raw_id_fields = ('release', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['release', 'instance'],
    }


admin.site.register(DeploymentReport, DeploymentReportAdmin)
