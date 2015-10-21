"""PDT admin dashboard."""

from django.utils.translation import ugettext_lazy as _
from grappelli.dashboard import modules, Dashboard
from django.core.urlresolvers import reverse


class CustomIndexDashboard(Dashboard):

    """Custom index dashboard for www."""

    def init_with_context(self, context):
        """Add dashboard items."""
        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Deployment and migration data'),
            collapsible=False,
            column=1,
            models=('pdt.core.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Notifications'),
            collapsible=False,
            column=1,
            models=('post_office.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append an app list module for "Configuration"
        self.children.append(modules.ModelList(
            _('Configuration'),
            column=1,
            collapsible=False,
            models=('constance.*',),
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Links'),
            column=2,
            children=[
                {
                    'title': _('Browsable API'),
                    'url': '/api',
                    'external': False,
                },
                {
                    'title': _('Release notes'),
                    'url': reverse('release-notes-overview'),
                    'external': False,
                },
            ]
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
