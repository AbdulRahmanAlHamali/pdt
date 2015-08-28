"""PDT admin filters."""
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from taggit_helpers import TaggitListFilter

from pdt.core.models import Release


def release_filter(column_name='release__number'):
    """Get release filter class."""
    class ReleaseFilter(admin.SimpleListFilter):

        """Filter by release number."""

        title = _('Release')
        parameter_name = 'release'

        def lookups(self, request, model_admin):
            return [
                (release.number, str(release)) for release in
                Release.objects.order_by('number').all()]

        def queryset(self, request, queryset):
            if self.value() is not None:
                return queryset.filter(**{column_name: self.value()})

    return ReleaseFilter


class ExcludeTaggitListFilter(TaggitListFilter):

    """Filter records by excluded Taggit tags for the current model only."""

    title = 'Exclude tags'
    parameter_name = 'exclude_tag'

    def queryset(self, request, queryset):
        """Exclude items with given tag."""
        if self.value() is not None:
            return queryset.filter(~Q(tags__name=self.value()))
