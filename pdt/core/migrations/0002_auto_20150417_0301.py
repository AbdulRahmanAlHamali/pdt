# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostDeployMigrationStep',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField(choices=[('sql', 'SQL'), ('python', 'Python')], max_length=10)),
                ('code', models.TextField()),
                ('path', models.CharField(blank=True, null=True, max_length=255)),
                ('position', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['position'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PreDeployMigrationStep',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField(choices=[('sql', 'SQL'), ('python', 'Python')], max_length=10)),
                ('code', models.TextField()),
                ('path', models.CharField(blank=True, null=True, max_length=255)),
                ('position', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['position'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='migration',
            name='code',
        ),
        migrations.RemoveField(
            model_name='migration',
            name='sql',
        ),
        migrations.AlterField(
            model_name='deploymentreport',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='migrationreport',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='release',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='predeploymigrationstep',
            name='migration',
            field=models.ForeignKey(related_name='pre_deploy_steps', to='core.Migration'),
        ),
        migrations.AddField(
            model_name='postdeploymigrationstep',
            name='migration',
            field=models.ForeignKey(related_name='post_deploy_steps', to='core.Migration'),
        ),
    ]
