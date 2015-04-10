"""PDT url configuration."""
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^api/', include('pdt.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^', include(admin.site.urls)),
]
