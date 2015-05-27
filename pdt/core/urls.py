"""PDT url configuration."""
from django.conf.urls import url

urlpatterns = [
    url(r'release-notes/(?P<release_number>[0-9]+)$', view='pdt.core.admin.generate_release_notes',
        name='release-notes'),
]
