"""PDT API views."""
from django.db.models import Q
from django.utils import timezone

import django_filters
from rest_framework import serializers, viewsets

from pdt.core.models import (
    Release,
    Instance,
    CIProject,
    Migration,
    MigrationReport,
    Case,
    DeploymentReport,
)


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):

    """Release serializer."""

    class Meta:
        model = Release
        fields = ('id', 'name', 'datetime')


class ReleaseViewSet(viewsets.ModelViewSet):

    """Return a list of all releases in the system.

    Filters (via **`<parameter>`** query string arguments):

    * name
    * date

    Orderings (via **`order_by`** query string parameter):

    * name
    * date
    """

    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    filter_fields = ('name', 'datetime')
    ordering_fields = ('name', 'datetime')
    ordering = ('name',)


class CIProjectFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom ci_project field handling."""

    class CIProjectSerializer(serializers.ModelSerializer):

        name = serializers.CharField()

        class Meta:
            model = CIProject
            fields = ('id', 'name', 'description')
            extra_kwargs = {
                'id': {'read_only': True},
                'name': {'read_only': True},
                'description': {'read_only': True},
            }

    ci_project = CIProjectSerializer()

    def validate_ci_project(self, value):
        """Validate ci_project complex type."""
        name = value['name']
        try:
            value, _ = CIProject.objects.get_or_create(name=name)
        except Exception as e:  # pragma: no cover
            raise serializers.ValidationError(e)
        return value


class InstanceSerializer(CIProjectFieldMixin):

    """Instance serializer."""

    class Meta:
        model = Instance
        fields = ('id', 'name', 'description', 'ci_project')


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


class CIProjectSerializer(serializers.HyperlinkedModelSerializer):

    """CI Project serializer."""

    class Meta:
        model = CIProject
        fields = ('id', 'name', 'description')


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


class CaseSerializer(CIProjectFieldMixin):

    """Case serializer."""

    class Meta:
        model = Case
        fields = ('id', 'title', 'description', 'project', 'release', 'ci_project')


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


class CaseFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom case field handling."""

    class CaseSerializer(serializers.ModelSerializer):

        id = serializers.IntegerField()

        class Meta:
            model = Case
            fields = ('id', 'title', 'description', 'ci_project')
            extra_kwargs = {
                'title': {'read_only': True},
                'description': {'read_only': True},
                'ci_project': {'read_only': True, 'source': 'ci_project.name'},
            }

    case = CaseSerializer()

    def validate_case(self, value):
        """Validate case complex type."""
        name = value['id']
        try:
            value, _ = Case.objects.get_or_create_from_fogbugz(case_id=name)
        except Exception as e:  # pragma: no cover
            raise serializers.ValidationError(e)
        return value


class MigrationSerializer(CaseFieldMixin):

    """Migration serializer."""

    class MigrationReportSerializer(serializers.ModelSerializer):

        ci_project = serializers.CharField(source='instance.ci_project.name')
        instance = serializers.CharField(source='instance.name')

        class Meta:
            model = MigrationReport
            fields = ('id', 'ci_project', 'instance', 'status', 'datetime', 'log')

    migration_reports = MigrationReportSerializer(source='migrationreport_set', read_only=True, many=True)

    class Meta:
        model = Migration
        fields = ('id', 'uid', 'case', 'category', 'sql', 'code', 'migration_reports')

    def create(self, validated_data):
        """Create or update the instance due to unique key on case."""
        try:
            instance = Migration.objects.get(
                case=validated_data['case'])
            return self.update(instance, validated_data)
        except Migration.DoesNotExist:
            return super(MigrationSerializer, self).create(validated_data)


class MigrationFilter(django_filters.FilterSet):

    """Migration filter to allow lookups for case, status, ci_project and instance."""

    case = django_filters.NumberFilter(name="case__id", lookup_type='exact')
    status = django_filters.CharFilter(name="migrationreport__status")
    exclude_status = django_filters.MethodFilter(action="filter_exclude_status")
    ci_project = django_filters.CharFilter(
        name="case__ci_project__name", lookup_type='exact')
    instance = django_filters.CharFilter(name="migrationreport__instance__name", lookup_type='exact')

    class Meta:
        model = Migration
        fields = ['uid', 'case', 'category', 'ci_project', 'instance', 'status', 'exclude_status']

    def filter_exclude_status(self, queryset, value):
        """Implement ``exclude`` filter by status."""
        return queryset.filter(Q(migrationreport__status__gt=value) | Q(migrationreport__status__lt=value))


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

    queryset = Migration.objects.all()
    serializer_class = MigrationSerializer
    ordering_fields = ('case', 'category')
    ordering = ('case', 'id')
    filter_class = MigrationFilter


class InstanceFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom instance field handling."""

    class InstanceSerializer(CIProjectFieldMixin):

        name = serializers.CharField()

        class Meta:
            model = Instance
            validators = []
            fields = ('id', 'name', 'ci_project', 'description')
            extra_kwargs = {
                'id': {'read_only': True},
                "name": {'read_only': True},
                "ci_project": {'read_only': True},
                'description': {'read_only': True}
            }

    instance = InstanceSerializer()

    def validate_instance(self, value):
        """Validate instance complex type."""
        name = value['name']
        try:
            value, _ = Instance.objects.get_or_create(name=name, ci_project=value['ci_project'])
        except Exception as e:  # pragma: no cover
            raise serializers.ValidationError(e)
        return value


class MigrationReportSerializer(InstanceFieldMixin):

    """Migration report serializer."""

    class MigrationSerializer(CaseFieldMixin):

        class Meta:
            model = Migration
            fields = ('id', 'case', 'category')
            extra_kwargs = {
                'id': {'read_only': True},
                'case': {'read_only': True},
                'category': {'read_only': True}
            }

    migration = MigrationSerializer()

    class Meta:
        model = MigrationReport
        fields = ('id', 'migration', 'instance', 'status', 'datetime', 'log')
        validators = []
        extra_kwargs = {
            'datetime': {'default': lambda: timezone.localtime(timezone.now())},
        }

    def validate_migration(self, value):
        """Validate migration complex type."""
        case = value['case']
        try:
            value = Migration.objects.get(case=case)
        except Exception as e:
            raise serializers.ValidationError(e)
        return value

    def create(self, validated_data):
        """Create or update the instance due to unique key on migration and instance."""
        try:
            instance = MigrationReport.objects.get(
                migration=validated_data['migration'], instance=validated_data['instance'])
            res = self.update(instance, validated_data)
            # to get timezone-aware datetime
            res.refresh_from_db()
            return res
        except MigrationReport.DoesNotExist:
            return super(MigrationReportSerializer, self).create(validated_data)


class MigrationReportViewSet(viewsets.ModelViewSet):

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


class ReleaseFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom release field handling."""

    class ReleaseSerializer(serializers.ModelSerializer):

        name = serializers.CharField()

        class Meta:
            model = Release
            fields = ('id', 'name', 'datetime')
            extra_kwargs = {
                'id': {'read_only': True},
                'description': {'read_only': True},
                'datetime': {'read_only': True}
            }

    release = ReleaseSerializer()

    def validate_release(self, value):
        """Validate release complex type."""
        name = value['name']
        try:
            value, _ = Release.objects.get_or_create(name=name)
        except Exception as e:  # pragma: no cover
            raise serializers.ValidationError(e)
        return value


class DeploymentReportSerializer(ReleaseFieldMixin, InstanceFieldMixin, serializers.HyperlinkedModelSerializer):

    """Deployment report serializer."""

    class Meta:
        model = DeploymentReport
        fields = ('id', 'release', 'instance', 'status', 'datetime', 'log')


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
