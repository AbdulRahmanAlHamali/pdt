"""PDT core case edit admin interface."""
from django.contrib import admin

from ..models import CaseEdit

from .columns import case_column


class CaseEditAdmin(admin.ModelAdmin):

    """Case edit admin interface class."""

    list_display = ('id', case_column(), 'type', 'params')
    list_filter = ('case__id', 'type')
    raw_id_fields = ('case',)
    autocomplete_lookup_fields = {
        'fk': ['case'],
    }


admin.site.register(CaseEdit, CaseEditAdmin)
