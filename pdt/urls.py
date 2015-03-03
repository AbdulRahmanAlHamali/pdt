"""PDT url configuration."""
from django.conf.urls import include, url
from django.contrib import admin


admin.site.site_header = 'Paylogic Deployment Tool Admin'

urlpatterns = [
    url(r'^api/', include('pdt.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(admin.site.urls)),
]
