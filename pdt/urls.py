"""PDT url configuration."""
from django.conf.urls import include, url
from django.contrib import admin
from adminplus.sites import AdminSitePlus

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = [
    url(r'^api/', include('pdt.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^core/', include('pdt.core.urls')),
    url(r'^', include(admin.site.urls)),
]
