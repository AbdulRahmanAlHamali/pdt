"""PDT admin dashboard."""

from django.utils.translation import ugettext_lazy as _
from grappelli.dashboard import modules, Dashboard


class CustomIndexDashboard(Dashboard):

    """Custom index dashboard for www."""

    def init_with_context(self, context):

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('AppList: Applications'),
            collapsible=False,
            column=1,
            exclude=('django.contrib.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('ModelList: Administration'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
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
            ]
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
