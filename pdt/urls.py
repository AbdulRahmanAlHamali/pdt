"""PDT url configuration."""
from django.conf.urls import include, url
from django.contrib import admin
from django.utils.safestring import mark_safe

admin.site.site_header = mark_safe(
    'Paylogic Deployment Tool Admin (<a href="/api" style="text-decoration: underline;">see API</a>)')
admin.site.index_title = 'Dashboard'


urlpatterns = [
    url(r'^api/', include('pdt.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(admin.site.urls)),
]
