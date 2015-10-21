"""PDT API serializers."""
import logging

from django.utils import timezone
from django.db.models import Q

from rest_framework import serializers

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

logger = logging.getLogger(__name__)


class ReleaseSerializer(serializers.HyperlinkedModelSerializer):

    """Release serializer."""

    class Meta:
        model = Release
        fields = ('id', 'number', 'datetime')


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
            logger.exception('Failed to get or create the CI project')
            raise serializers.ValidationError(e)
        return value


class CIProjectsFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom ci_projects field handling."""

    class CIProjectSerializer(serializers.ModelSerializer):

        class Meta:
            model = CIProject
            fields = ('id', 'name', 'description')
            extra_kwargs = {
                'id': {'read_only': True},
                'name': {'validators': []},
                'description': {'read_only': True},
            }

    ci_projects = CIProjectSerializer(many=True, required=False)

    def validate_ci_projects(self, values):
        """Validate ci_project complex type."""
        result = []
        for value in values:
            name = value['name']
            try:
                value, _ = CIProject.objects.get_or_create(name=name)
            except Exception as e:  # pragma: no cover
                logger.exception('Failed to get or create the CI project')
                raise serializers.ValidationError(e)
            result.append(value)
        return result


class InstanceSerializer(CIProjectsFieldMixin):

    """Instance serializer."""

    class Meta:
        model = Instance
        fields = ('id', 'name', 'description', 'ci_projects')

    def create(self, validated_data):
        """Create or update the instance due to unique key on case."""
        ci_projects = validated_data.pop('ci_projects')
        instance = super(InstanceSerializer, self).create(validated_data)
        instance.save()
        instance.ci_projects = ci_projects
        return instance


class CIProjectSerializer(serializers.HyperlinkedModelSerializer):

    """CI project serializer."""

    class Meta:
        model = CIProject
        fields = ('id', 'name', 'description')


class MigrationStepListSerializer(serializers.ListSerializer):  # pylint: disable=W0223

    """List serializer which filters out applied steps."""

    def to_representation(self, data):
        """Filter out applied steps."""
        exclude_status = self.context['request'].REQUEST.get('exclude_status')
        if exclude_status:
            data = data.filter(
                ~Q(reports__status=exclude_status)
            )
        return super(MigrationStepListSerializer, self).to_representation(data)


class MigrationStepSerializer(serializers.HyperlinkedModelSerializer):

    """Migration step serializer."""

    class Meta:
        fields = ('id', 'position', 'type', 'code', 'path')
        list_serializer_class = MigrationStepListSerializer


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


class CaseSerializer(CIProjectFieldMixin):

    """Case serializer."""

    class Meta:
        model = Case
        fields = ('id', 'title', 'description', 'project', 'release', 'ci_project', 'revision')


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


class InstanceFieldMixin(serializers.HyperlinkedModelSerializer):

    """Add custom instance field handling."""

    class InstanceSerializer(CIProjectsFieldMixin):

        name = serializers.CharField()

        class Meta:
            model = Instance
            validators = []
            fields = ('id', 'name', 'ci_projects', 'description')
            extra_kwargs = {
                'id': {'read_only': True},
                "name": {'read_only': True},
                "ci_projects": {'read_only': True},
                'description': {'read_only': True}
            }

    instance = InstanceSerializer()

    def validate_instance(self, value):
        """Validate instance complex type."""
        name = value['name']
        try:
            value = Instance.objects.get(name=name)
        except Exception as e:  # pragma: no cover
            logger.exception('Failed to get an instance')
            raise serializers.ValidationError(e)
        return value


class MigrationSerializer(CaseFieldMixin):

    """Migration serializer."""

    class MigrationReportSerializer(InstanceFieldMixin):

        class Meta:
            model = MigrationReport
            fields = ('id', 'instance', 'status', 'datetime', 'log')

    pre_deploy_steps = PreDeployMigrationStepSerializer(many=True)
    post_deploy_steps = PostDeployMigrationStepSerializer(many=True)
    final_steps = FinalMigrationStepSerializer(many=True)
    reports = MigrationReportSerializer(read_only=True, many=True)
    parent = serializers.CharField(source='parent.uid', allow_null=True)
    release = ReleaseSerializer(source='case.release', read_only=True)

    class Meta:
        model = Migration
        fields = (
            'id', 'uid', 'parent', 'case', 'category', 'pre_deploy_steps', 'post_deploy_steps', 'final_steps',
            'reports', 'reviewed', 'release')
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

    cases = CaseSerializer(many=True, write_only=True)

    class Meta:
        model = DeploymentReport
        fields = ('id', 'instance', 'status', 'datetime', 'log', 'cases')

    def create(self, validated_data):
        """Create or update the instance due to unique key on case."""
        cases = validated_data.pop('cases')
        report = super(DeploymentReportSerializer, self).create(validated_data)
        report.cases.clear()
        report_cases = []
        for case_data in cases:
            case, _ = Case.objects.get_or_create_from_fogbugz(case_data['id'])
            report_cases.append(case)
        report.cases = report_cases
        report.save()
        return report
