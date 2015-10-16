"""PDT core CI project admin interface."""
from django.contrib import admin

from ..models import CIProject
from .columns import instances_column


class CIProjectAdmin(admin.ModelAdmin):

    """CI Project admin interface class."""

    list_display = ('id', 'name', 'description', instances_column())
    list_filter = ('instances__name',)
    search_fields = ('id', 'name', 'description')


admin.site.register(CIProject, CIProjectAdmin)
