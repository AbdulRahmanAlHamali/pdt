"""PDT core admin class mixins."""
from django import forms
from django.utils.translation import ugettext_lazy as _

import embedded_media as emb

from ansi2html import Ansi2HTMLConverter
from ansi2html.style import get_styles


ACE_WIDGET_PARAMS = dict(showprintmargin=False, width='100%')


class TinyMCEMixin(object):

    """Mixin to add tinymce editor."""

    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/grappelli/tinymce_setup/tinymce_setup.js',
        ]


class LogAdminMixin(object):

    """Mixin for adding rendered log field."""

    def __init__(self, *args, **kwargs):
        """Assign excluded fields list so it's instance attribute."""
        self.exclude = self.exclude
        super(LogAdminMixin, self).__init__(*args, **kwargs)

    @property
    def media(self):
        """Add inline styling for rendered."""
        return super(LogAdminMixin, self).media + forms.Media(css={'all': (
            emb.CSS("\n".join(str(style) for style in get_styles(dark_bg=False))),
            emb.CSS("""
                .grp-readonly .ansi2html-content {
                    white-space: pre-wrap !important;
                    word-wrap: break-word;
                    font-family: monospace;
                }
                .ansi2html-container {
                    max-height: 500px;
                    overflow: auto;
                }
            """))})

    def get_readonly_fields(self, request, obj):
        """Make log field readonly if it's an edit form."""
        self.exclude = ('log',) if obj and obj.id else ('rendered_log', )
        return ('rendered_log', ) if obj and obj.id else ()

    def rendered_log(self, instance):
        """Render ansi colors as html."""
        converted = Ansi2HTMLConverter(dark_bg=False).convert(instance.log, full=False)
        return '<div class="ansi2html-container"><pre class="ansi2html-content">{0}</pre><div>'.format(
            converted.replace('/span> <span', '/span>&nbsp;<span')
        )
    rendered_log.short_description = _('Log')
    rendered_log.allow_tags = True
