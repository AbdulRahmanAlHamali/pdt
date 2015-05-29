"""PDT url configuration."""
from django.conf.urls import url

urlpatterns = [
    url(r'release-notes/?$', view='pdt.core.admin.release_notes_overview',
        name='release-notes-overview'),
    url(r'release-notes/(?P<release_number>[0-9]+)/?$', view='pdt.core.admin.release_notes',
        name='release-notes'),
]
