"""PDT core CI project admin interface."""
from django.contrib import admin

from ..models import CIProject


class CIProjectAdmin(admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name', 'description')


admin.site.register(CIProject, CIProjectAdmin)
