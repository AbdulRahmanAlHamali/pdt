"""PDT API urls."""
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from pdt.core.models import (
    Release,
    Instance,
    Project,
    Migration,
    MigrationReport,
    Case,
    DeploymentReport,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):

    """User serializer."""

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ModelViewSet):

    """User viewset."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):

    """Release serializer."""

    class Meta:
        model = Release
        fields = ('name', 'date')


class ReleaseViewSet(viewsets.ModelViewSet):

    """Relase viewset."""

    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer


class InstanceSerializer(serializers.HyperlinkedModelSerializer):

    """Instance serializer."""

    class Meta:
        model = Instance
        fields = ('name', 'description')


class InstanceViewSet(viewsets.ModelViewSet):

    """Instance viewset."""

    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    """Project serializer."""

    class Meta:
        model = Project
        fields = ('name', 'description')


class ProjectViewSet(viewsets.ModelViewSet):

    """Project viewset."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class MigrationSerializer(serializers.HyperlinkedModelSerializer):

    """Migration serializer."""

    class Meta:
        model = Migration
        fields = ('release', 'project', 'category', 'sql', 'code')


class MigrationViewSet(viewsets.ModelViewSet):

    """Migration viewset."""

    queryset = Migration.objects.all()
    serializer_class = MigrationSerializer


class MigrationReportSerializer(serializers.HyperlinkedModelSerializer):

    """Migration report serializer."""

    class Meta:
        model = MigrationReport
        fields = ('migration', 'instance', 'status', 'datetime', 'log')


class MigrationReportViewSet(viewsets.ModelViewSet):

    """Migration report viewset."""

    queryset = MigrationReport.objects.all()
    serializer_class = MigrationReportSerializer


class CaseSerializer(serializers.HyperlinkedModelSerializer):

    """Case serializer."""

    class Meta:
        model = Case
        fields = ('id', 'title', 'description', 'project', 'release')


class CaseViewSet(viewsets.ModelViewSet):

    """Case viewset."""

    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class DeploymentReportSerializer(serializers.HyperlinkedModelSerializer):

    """Deployment report serializer."""

    class Meta:
        model = DeploymentReport
        fields = ('release', 'instance', 'status', 'datetime', 'log')


class DeploymentReportViewSet(viewsets.ModelViewSet):

    """DeploymentReport report viewset."""

    queryset = DeploymentReport.objects.all()
    serializer_class = DeploymentReportSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'releases', ReleaseViewSet)
router.register(r'instances', InstanceViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'migrations', MigrationViewSet)
router.register(r'migration-reports', MigrationReportViewSet)
router.register(r'cases', CaseViewSet)
router.register(r'deployment-reports', DeploymentReportViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
]
