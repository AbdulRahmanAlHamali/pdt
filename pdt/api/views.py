"""PDT API views."""
import logging

from django.db.models import Q
from django.utils import timezone

import django_filters
from rest_framework import serializers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from pdt.core.models import (
    Case,
    CIProject,
    DeploymentReport,
    FinalMigrationStep,
    Instance,
    Migration,
    MigrationReport,
    MigrationStep,
    MigrationStepReport,
    PostDeployMigrationStep,
    PreDeployMigrationStep,
    Release,
)

from pdt.core.tasks import update_case_from_fogbugz

logger = logging.getLogger(__name__)


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):

    """Release serializer."""

    class Meta:
        model = Release
        fields = ('id', 'number', 'datetime')


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


class CIProjectFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom ci_project field handling."""

    class CIProjectSerializer(serializers.ModelSerializer):

        class Meta:
            model = CIProject
            fields = ('id', 'name', 'description')
            extra_kwargs = {
                'id': {'read_only': True},
                'name': {'validators': []},
                'description': {'read_only': True},
            }

    ci_project = CIProjectSerializer()

    def validate_ci_project(self, value):
        """Validate ci_project complex type."""
        name = value['name']
        try:
            value, _ = CIProject.objects.get_or_create(name=name)
        except Exception as e:  # pragma: no cover
            logger.exception('Failed to get or create the ci project')
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


class MigrationStepSerializer(serializers.HyperlinkedModelSerializer):

    """Migration step serializer."""

    class Meta:
        fields = ('id', 'position', 'type', 'code', 'path')


class PreDeployMigrationStepSerializer(MigrationStepSerializer):

    """Pre-deploy phase migration step serializer."""

    class Meta(MigrationStepSerializer.Meta):
        model = PreDeployMigrationStep


class PostDeployMigrationStepSerializer(MigrationStepSerializer):

    """Post-deploy phase migration step serializer."""

    class Meta(MigrationStepSerializer.Meta):
        model = PostDeployMigrationStep


class FinalMigrationStepSerializer(MigrationStepSerializer):

    """Final phase migration step serializer."""

    class Meta(MigrationStepSerializer.Meta):
        model = FinalMigrationStep


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

    @detail_route(methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def trigger_sync(self, request, pk=None):
        """Trigger case sync with the issue tracking system."""
        update_case_from_fogbugz.delay(case_id=pk)
        return Response({'status': 'sync is triggered successfully'})


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
            logger.exception('Failed to get or create the case')
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

    pre_deploy_steps = PreDeployMigrationStepSerializer(many=True)
    post_deploy_steps = PostDeployMigrationStepSerializer(many=True)
    final_steps = FinalMigrationStepSerializer(many=True)
    reports = MigrationReportSerializer(read_only=True, many=True)
    parent = serializers.CharField(source='parent.uid', allow_null=True)

    class Meta:
        model = Migration
        fields = (
            'id', 'uid', 'parent', 'case', 'category', 'pre_deploy_steps', 'post_deploy_steps', 'final_steps',
            'reports', 'reviewed')
        extra_kwargs = {
            'uid': {'validators': []},
            'category': {'read_only': True},
            'reviewed': {'read_only': True},
        }

    def validate_parent(self, value):
        """Validate parent field."""
        if value:
            try:
                value = Migration.objects.get(uid=value)
            except Migration.DoesNotExist:  # pragma: no cover
                message = 'Failed to get the parent migration'
                logger.exception(message)
                raise serializers.ValidationError(message)
        return value

    def create(self, validated_data):
        """Create or update the instance due to unique key on case."""
        pre_deploy_steps = validated_data.pop('pre_deploy_steps')
        post_deploy_steps = validated_data.pop('post_deploy_steps')
        final_steps = validated_data.pop('final_steps')
        parent = validated_data.pop('parent')['uid']
        try:
            instance = Migration.objects.get(
                case=validated_data['case'])
            migration = self.update(instance, validated_data)
            migration.pre_deploy_steps.get_queryset().delete()
            migration.post_deploy_steps.get_queryset().delete()
            migration.final_steps.get_queryset().delete()
        except Migration.DoesNotExist:
            migration = super(MigrationSerializer, self).create(validated_data)
        migration.parent = parent
        migration.save()
        pre_deploy_steps = [
            PreDeployMigrationStep.objects.create(**dict(step_data, migration=migration, position=index))
            for index, step_data in enumerate(pre_deploy_steps)
        ]
        post_deploy_steps = [
            PostDeployMigrationStep.objects.create(**dict(step_data, migration=migration, position=index))
            for index, step_data in enumerate(post_deploy_steps)
        ]
        final_steps = [
            FinalMigrationStep.objects.create(**dict(step_data, migration=migration, position=index))
            for index, step_data in enumerate(final_steps)
        ]
        return migration


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
            value = Instance.objects.get(name=name, ci_project=value['ci_project'])
        except Exception as e:  # pragma: no cover
            logger.exception('Failed to get an instance')
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
            'log': {'read_only': True},
            'status': {'read_only': True}
        }


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


class MigrationStepReportSerializer(serializers.HyperlinkedModelSerializer):

    """Migration step report serializer."""

    class MigrationReportSerializer(InstanceFieldMixin):

        class MigrationSerializer(serializers.ModelSerializer):

            class Meta:
                model = Migration
                fields = ('id', 'uid', 'case', 'category')
                extra_kwargs = {
                    'id': {'read_only': True},
                    'case': {'read_only': True},
                    'category': {'read_only': True},
                    'uid': {'validators': []},
                }

        class Meta:
            model = MigrationReport
            validators = []
            fields = ('id', 'migration', 'instance')

        migration = MigrationSerializer()

        def validate_migration(self, value):
            """Validate migration complex type."""
            try:
                value = Migration.objects.get(uid=value['uid'])
            except Exception as e:  # pragma: no cover
                logger.exception('Failed to get migration')
                raise serializers.ValidationError(e)
            return value

    report = MigrationReportSerializer()

    class MigrationStepSerializer(serializers.ModelSerializer):

        class Meta:
            model = MigrationStep
            fields = ('id',)
            extra_kwargs = {
                'id': {'read_only': False},
            }

    step = MigrationStepSerializer()

    class Meta:
        model = MigrationStepReport
        fields = ('id', 'report', 'step', 'status', 'datetime', 'log')
        validators = []
        extra_kwargs = {
            'datetime': {'default': lambda: timezone.localtime(timezone.now())},
        }

    def validate_step(self, value):
        """Validate step complex type."""
        try:
            value = MigrationStep.objects.get(id=value['id'])
        except Exception as e:  # pragma: no cover
            logger.exception('Failed to get migration step')
            raise serializers.ValidationError(e)
        return value

    def validate_report(self, value):
        """Validate migration complex type."""
        migration = value['migration']
        instance = value['instance']
        try:
            value, _ = MigrationReport.objects.get_or_create(migration=migration, instance=instance)
        except Exception as e:
            logger.exception('Failed to get or create the migration report')
            raise serializers.ValidationError(e)
        return value

    def create(self, validated_data):
        """Create or update the instance due to unique key on migration and instance."""
        try:
            instance = MigrationStepReport.objects.get(
                report=validated_data['report'], step=validated_data['step'])
            res = self.update(instance, validated_data)
            # to get timezone-aware datetime
            res.refresh_from_db()
            return res
        except MigrationStepReport.DoesNotExist:
            return super(MigrationStepReportSerializer, self).create(validated_data)


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


class ReleaseFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom release field handling."""

    class ReleaseSerializer(serializers.ModelSerializer):

        class Meta:
            model = Release
            fields = ('id', 'number', 'datetime')
            extra_kwargs = {
                'id': {'read_only': True},
                'description': {'read_only': True},
                'datetime': {'read_only': True},
                'number': {'validators': []}
            }

    release = ReleaseSerializer()

    def validate_release(self, value):
        """Validate release complex type."""
        number = value['number']
        try:
            value = Release.objects.get(number=number)
        except Exception as e:  # pragma: no cover
            logger.exception('Failed to get the release')
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
