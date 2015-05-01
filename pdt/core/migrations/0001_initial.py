# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(blank=True)),
                ('project', models.CharField(max_length=255, blank=True)),
                ('area', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CIProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True, unique=True)),
                ('description', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeploymentReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=3, choices=[('dpl', 'Deployed'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('log', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['release', 'instance', 'datetime', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('ci_project', models.ForeignKey(to='core.CIProject')),
            ],
        ),
        migrations.CreateModel(
            name='Migration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=255, unique=True)),
                ('category', models.CharField(max_length=3, db_index=True, default='onl', choices=[('off', 'Offline'), ('onl', 'Online')])),
                ('reviewed', models.BooleanField(db_index=True, default=False)),
                ('case', models.OneToOneField(to='core.Case')),
            ],
        ),
        migrations.CreateModel(
            name='MigrationReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=3, choices=[('apl', 'Applied'), ('prt', 'Applied partially'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('log', models.TextField(blank=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
                ('migration', models.ForeignKey(to='core.Migration', related_name='reports')),
            ],
            options={
                'ordering': ['migration', 'instance', 'datetime', 'id'],
            },
        ),
        migrations.CreateModel(
            name='MigrationStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=10, choices=[('mysql', 'MySQL'), ('pgsql', 'pgSQL'), ('python', 'Python'), ('sh', 'Shell')])),
                ('code', models.TextField()),
                ('path', models.CharField(max_length=255, blank=True, null=True)),
                ('position', models.PositiveSmallIntegerField(db_index=True)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='MigrationStepReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=3, db_index=True, choices=[('apl', 'Applied'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('log', models.TextField(blank=True)),
                ('report', models.ForeignKey(to='core.MigrationReport', related_name='step_reports')),
            ],
            options={
                'ordering': ['report', 'step', 'datetime', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True, unique=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='PostDeployMigrationStep',
            fields=[
                ('migrationstep_ptr', models.OneToOneField(to='core.MigrationStep', serialize=False, auto_created=True, parent_link=True, primary_key=True)),
                ('migration', models.ForeignKey(to='core.Migration', related_name='post_deploy_steps')),
            ],
            bases=('core.migrationstep',),
        ),
        migrations.CreateModel(
            name='PreDeployMigrationStep',
            fields=[
                ('migrationstep_ptr', models.OneToOneField(to='core.MigrationStep', serialize=False, auto_created=True, parent_link=True, primary_key=True)),
                ('migration', models.ForeignKey(to='core.Migration', related_name='pre_deploy_steps')),
            ],
            bases=('core.migrationstep',),
        ),
        migrations.AddField(
            model_name='migrationstepreport',
            name='step',
            field=models.ForeignKey(to='core.MigrationStep'),
        ),
        migrations.AlterIndexTogether(
            name='migrationstep',
            index_together=set([('id', 'position')]),
        ),
        migrations.AddField(
            model_name='deploymentreport',
            name='instance',
            field=models.ForeignKey(to='core.Instance'),
        ),
        migrations.AddField(
            model_name='deploymentreport',
            name='release',
            field=models.ForeignKey(to='core.Release'),
        ),
        migrations.AddField(
            model_name='case',
            name='ci_project',
            field=models.ForeignKey(to='core.CIProject'),
        ),
        migrations.AddField(
            model_name='case',
            name='release',
            field=models.ForeignKey(to='core.Release'),
        ),
        migrations.AlterUniqueTogether(
            name='migrationstepreport',
            unique_together=set([('report', 'step')]),
        ),
        migrations.AlterIndexTogether(
            name='migrationstepreport',
            index_together=set([('report', 'step', 'status'), ('report', 'step', 'datetime', 'id')]),
        ),
        migrations.AlterUniqueTogether(
            name='migrationreport',
            unique_together=set([('migration', 'instance')]),
        ),
        migrations.AlterIndexTogether(
            name='migrationreport',
            index_together=set([('migration', 'instance', 'datetime', 'id'), ('id', 'migration')]),
        ),
        migrations.AlterIndexTogether(
            name='migration',
            index_together=set([('id', 'uid', 'case'), ('category', 'reviewed')]),
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([('name', 'ci_project')]),
        ),
        migrations.AlterIndexTogether(
            name='instance',
            index_together=set([('id', 'name')]),
        ),
        migrations.AlterIndexTogether(
            name='deploymentreport',
            index_together=set([('release', 'instance', 'datetime', 'id')]),
        ),
        migrations.AlterIndexTogether(
            name='case',
            index_together=set([('ci_project', 'release'), ('id', 'title')]),
        ),
    ]
