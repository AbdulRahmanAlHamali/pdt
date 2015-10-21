"""PDT core instance admin interface."""
from django.contrib import admin

from ..models import (
    NotificationTemplate,
)

from post_office.models import EmailTemplate
from post_office.fields import CommaSeparatedEmailField
from post_office.admin import (
    CommaSeparatedEmailWidget,
    EmailTemplateAdmin as BaseEmailTemplateAdmin,
)
from reversion.admin import VersionAdmin

EmailTemplate.__str__ = lambda self: self.name

EmailTemplate.autocomplete_search_fields = staticmethod(lambda: ("id__iexact", "name__icontains",))


class EmailTemplateAdmin(VersionAdmin, BaseEmailTemplateAdmin):

    """Versioned email template admin."""

admin.site.unregister(EmailTemplate)
admin.site.register(EmailTemplate, EmailTemplateAdmin)


class NotificationTemplateAdmin(admin.ModelAdmin):

    """Notification template admin interface class."""

    list_display = ('id', 'from_email', 'to', 'cc', 'bcc', 'template')
    search_fields = ('id', 'from_email', 'to', 'cc', 'bcc', 'template')

    raw_id_fields = ('template',)
    autocomplete_lookup_fields = {
        'fk': ['template']
    }

    formfield_overrides = {
        CommaSeparatedEmailField: {'widget': CommaSeparatedEmailWidget}
    }

admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
