"""PDT url configuration."""
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin

from .admin import UserAdmin

admin.site = UserAdmin()
admin.autodiscover()

admin.site.index_title = _('Dashboard')

urlpatterns = [
    url(r'^api/', include('pdt.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^core/', include('pdt.core.urls')),
    url(r'^', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
