"""PDT core admin interface."""
import collections
import logging
import pprint

from django.template import Template, RequestContext
from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, get_object_or_404

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

    list_display = ('id', 'number', 'datetime')
    list_filter = ('datetime',)
    search_fields = ('id', 'number', 'datetime')

    def generate_release_notes(self, request, obj):
        """Redirect to a page with release notes for this release."""
        return redirect('release-notes', release_number=obj.number)
    generate_release_notes.label = _("Generate release notes")
    generate_release_notes.short_description = _("Redirect to the rendered release notes")

    objectactions = ['generate_release_notes']


admin.site.register(Release, ReleaseAdmin)


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

    return Template(config.RELEASE_NOTES_TEMPLATE).render(RequestContext(request, dict(
        release=release, categorized_cases=categorized_cases, categories=categories)))


def release_notes(request, release_number, **kwargs):
    """Release notes view."""
    release = get_object_or_404(Release.objects.filter(number=release_number))
    return HttpResponse(get_release_notes(request, release))


def release_notes_overview(request):
    """Release notes overview view."""
    notes = []
    for release in Release.objects.all().order_by('-number'):
        notes.append(get_release_notes(request, release))
    return HttpResponse(
        Template(config.RELEASE_NOTES_OVERVIEW_TEMPLATE).render(RequestContext(request, dict(
            categories=CaseCategory.objects.filter(is_default=False, is_hidden=False),
            notes=notes))))


class CIProjectAdmin(TinyMCEMixin, admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name', 'description')


admin.site.register(CIProject, CIProjectAdmin)


def ci_project(self):
    """Get CI project name."""
    return self.ci_project.name
ci_project.admin_order_field = 'ci_project__name'


class InstanceAdmin(TinyMCEMixin, admin.ModelAdmin):

    """Instance admin interface class."""

    list_display = ('id', 'name', 'description', ci_project)
    list_filter = ('ci_project__name',)
    search_fields = ('id', 'name', 'description')
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
    search_fields = ('id', 'type', 'script')
    autocomplete_lookup_fields = {
        'fk': ['migration'],
    }

admin.site.register(MigrationStep, MigrationStepAdmin)


def mark_migrations_reviewed(modeladmin, request, queryset):
    """Mark migrations reviewed."""
    queryset.update(reviewed=True)
mark_migrations_reviewed.short_description = _("Mark selected migrations as reviewed")


def mark_migrations_not_reviewed(modeladmin, request, queryset):
    """Mark migrations as not reviewed."""
    queryset.update(reviewed=False)
mark_migrations_not_reviewed.short_description = _("Mark selected migrations as not reviewed")


def applied_on(migration):
    """Migration applied on."""
    return mark_safe(
        ", ".join('<a href="{url}">{name}: {datetime}: {status}</a>'.format(
            url=reverse("admin:core_migrationreport_change", args=(report.id,)),
            name=report.instance.name, datetime=report.datetime, status=report.get_status_display()
        ) for report in migration.reports.all()))
applied_on.short_description = "Applied on"


def case_ci_project(self):
    """Get case ci project."""
    return self.case.ci_project.name
case_ci_project.admin_order_field = 'case__ci_project__name'


class MigrationAdmin(admin.ModelAdmin):

    """Migration admin interface class."""

    list_display = ('id', 'uid', case, case_ci_project, 'category', 'reviewed', applied_on)
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


def migration_uid(self):
    """Get migration uid."""
    return self.migration.uid
migration_uid.admin_order_field = 'migration__uid'


def migration_release_number(self):
    """Get migration release number."""
    return self.migration.case.release.number if self.migration.case.release else _('n/a')
migration_release_number.admin_order_field = 'migration__case__release__number'


class MigrationReportAdmin(admin.ModelAdmin):

    """MigrationReport admin interface class."""

    form = MigrationReportForm
    list_display = ('id', migration_uid, migration_case, migration_release_number, 'instance', 'status', 'datetime')
    list_filter = ('instance__name', 'status')
    search_fields = ('migration__uid', 'migration__case__id')
    raw_id_fields = ('migration', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['migration', 'instance'],
    }
    # readonly_fields = ('datetime', 'status')
    inlines = [MigrationStepReportInline]


admin.site.register(MigrationReport, MigrationReportAdmin)


def tags(obj):
    """Tags."""
    return ', '.join(tag.name for tag in obj.tags.all())


class CaseAdmin(TinyMCEMixin, admin.ModelAdmin):

    """Case admin interface class."""

    list_display = ('id', 'title', 'ci_project', 'release', 'project', 'area', tags)
    list_filter = ('ci_project__name', 'release', 'project', 'area')
    search_fields = ('id', 'title')
    raw_id_fields = ('ci_project', 'release')
    autocomplete_lookup_fields = {
        'fk': ['ci_project', 'release'],
    }


admin.site.register(Case, CaseAdmin)


class CaseEditAdmin(admin.ModelAdmin):

    """Case edit admin interface class."""

    list_display = ('id', 'case', 'type', 'params')
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
    list_display = ('id', 'release', 'instance', 'status', 'datetime')
    list_filter = ('release__number', 'instance__name', 'status')
    search_fields = ('release__number', 'instance__name')
    raw_id_fields = ('release', 'instance')
    autocomplete_lookup_fields = {
        'fk': ['release', 'instance'],
    }


admin.site.register(DeploymentReport, DeploymentReportAdmin)
