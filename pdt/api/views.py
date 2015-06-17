"""PDT API views."""
import logging

from django.db.models import Q

import django_filters
from rest_framework import (
    exceptions,
    viewsets,
)
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from pdt.core.models import (
    Case,
    CIProject,
    DeploymentReport,
    Instance,
    Migration,
    MigrationReport,
    MigrationStepReport,
    Release,
)
from pdt.core.tasks import update_case_from_fogbugz

from .serializers import (
    CaseSerializer,
    CIProjectSerializer,
    DeploymentReportSerializer,
    InstanceSerializer,
    MigrationReportSerializer,
    MigrationSerializer,
    MigrationStepReportSerializer,
    ReleaseSerializer,
)

logger = logging.getLogger(__name__)


class InstanceViewSet(viewsets.ModelViewSet):

    """Return a list of all instances in the system.

    Filters (via **`<parameter>`** query string arguments):

    * name

    Orderings (via **`order_by`** query string parameter):

    * name
    """

    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
    filter_fields = ('name',)
    ordering_fields = ('name',)
    ordering = ('name',)


class ReleaseViewSet(viewsets.ModelViewSet):

    """Return a list of all releases in the system.

    Filters (via **`<parameter>`** query string arguments):

    * number
    * date

    Orderings (via **`order_by`** query string parameter):

    * number
    * date
    """

    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    filter_fields = ('number', 'datetime')
    ordering_fields = ('number', 'datetime')
    ordering = ('number',)


class CIProjectViewSet(viewsets.ModelViewSet):

    """Return a list of all continuos integration projects in the system.

    Filters (via **`<parameter>`** query string arguments):

    * name

    Orderings (via **`order_by`** query string parameter):

    * name
    """

    queryset = CIProject.objects.all()
    serializer_class = CIProjectSerializer
    filter_fields = ('name',)
    ordering_fields = ('name',)
    ordering = ('name',)


class CaseViewSet(viewsets.ModelViewSet):

    """Return a list of all fogbugz cases in the system.

    Filters (via **`<parameter>`** query string arguments):

    * id
    * title
    * project
    * release

    Orderings (via **`order_by`** query string parameter):

    * id
    * title
    * project
    * release
    """

    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filter_fields = ('id', 'title', 'project', 'release', 'ci_project')
    ordering_fields = ('id', 'title', 'project', 'release', 'ci_project')
    ordering = ('id',)

    @detail_route(methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def trigger_sync(self, request, pk=None):
        """Trigger case sync with the issue tracking system."""
        update_case_from_fogbugz.delay(case_id=pk)
        return Response({'status': 'sync is triggered successfully'})


class MigrationFilter(django_filters.FilterSet):

    """Migration filter to allow lookups for case, status, ci_project."""

    case = django_filters.NumberFilter(name="case__id", lookup_type='exact')
    release = django_filters.CharFilter(name="case__release__number", lookup_type='lte')
    reviewed = django_filters.BooleanFilter(name="reviewed", lookup_type='exact')
    status = django_filters.CharFilter(name="reports__status")
    exclude_status = django_filters.MethodFilter(action="filter_exclude_status")
    ci_project = django_filters.CharFilter(
        name="case__ci_project__name", lookup_type='exact')
    instance = django_filters.MethodFilter(action="filter_instance")

    class Meta:
        model = Migration
        fields = [
            'uid', 'case', 'release', 'category', 'ci_project', 'instance', 'status', 'exclude_status', 'reviewed']

    def filter_exclude_status(self, queryset, value):
        """Implement ``exclude`` filter by status."""
        if not self.form.cleaned_data['instance']:
            raise exceptions.ValidationError('Instance is required to exclude status')
        return queryset.filter(
            Q(reports__status__gt=value) | Q(reports__status__lt=value) |
            Q(reports__isnull=True))

    def filter_instance(self, queryset, value):
        """Implement filter by instance."""
        return queryset.filter(
            Q(reports__instance__name=value) | Q(reports__isnull=True) | Q(case__ci_project__instances__name=value))


class MigrationViewSet(viewsets.ModelViewSet):

    """Return a list of all migrations in the system.

    Filters (via **`<parameter>`** query string arguments):

    * uid
    * case
    * category
    * status
    * exclude_status
    * ci_project
    * instance

    Orderings (via **`order_by`** query string parameter):

    * case
    * category
    """

    queryset = Migration.objects.all().distinct()
    serializer_class = MigrationSerializer
    ordering_fields = ('case', 'category')
    ordering = ('case', 'id')
    filter_class = MigrationFilter
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """Perform topological sort on returned migrations."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(Migration.objects.sort(queryset), many=True)
        return Response(serializer.data)


class MigrationReportViewSet(viewsets.ReadOnlyModelViewSet):

    """Return a list of all migration reports in the system.

    Filters (via **`<parameter>`** query string arguments):

    * migration
    * instance
    * status
    * datetime

    Orderings (via **`order_by`** query string parameter):

    * migration
    * instance
    * status
    * datetime
    """

    queryset = MigrationReport.objects.all()
    serializer_class = MigrationReportSerializer
    filter_fields = ('migration', 'instance', 'status', 'datetime')
    ordering_fields = ('migration', 'instance', 'status', 'datetime')
    ordering = ('migration', 'instance', 'datetime', 'id')


class MigrationStepReportViewSet(viewsets.ModelViewSet):

    """Return a list of all migration reports in the system.

    Filters (via **`<parameter>`** query string arguments):

    * migration
    * instance
    * status
    * datetime

    Orderings (via **`order_by`** query string parameter):

    * migration
    * instance
    * status
    * datetime
    """

    queryset = MigrationStepReport.objects.all()
    serializer_class = MigrationStepReportSerializer
    filter_fields = ('report', 'status', 'datetime')
    ordering_fields = ('report', 'status', 'datetime')
    ordering = ('report', 'datetime', 'id')


class DeploymentReportViewSet(viewsets.ModelViewSet):

    """Return a list of all deployment reports in the system.

    Filters (via **`<parameter>`** query string arguments):

    * release
    * instance
    * status
    * datetime

    Orderings (via **`order_by`** query string parameter):

    * release
    * instance
    * status
    * datetime
    """

    queryset = DeploymentReport.objects.all()
    serializer_class = DeploymentReportSerializer
    filter_fields = ('release', 'instance', 'status', 'datetime')
    ordering_fields = ('release', 'instance', 'status', 'datetime')
    ordering = ('release', 'instance', 'datetime', 'id')
