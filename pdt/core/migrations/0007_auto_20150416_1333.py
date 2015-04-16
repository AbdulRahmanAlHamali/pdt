# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150416_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostDeployMigrationStep',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.CharField(max_length=10, choices=[('sql', 'SQL'), ('python', 'Python')])),
                ('code', models.TextField()),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
                ('position', models.PositiveSmallIntegerField()),
                ('migration', models.ForeignKey(to='core.Migration')),
            ],
            options={
                'abstract': False,
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='PreDeployMigrationStep',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.CharField(max_length=10, choices=[('sql', 'SQL'), ('python', 'Python')])),
                ('code', models.TextField()),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
                ('position', models.PositiveSmallIntegerField()),
                ('migration', models.ForeignKey(to='core.Migration')),
            ],
            options={
                'abstract': False,
                'ordering': ['position'],
            },
        ),
        migrations.RemoveField(
            model_name='migrationstep',
            name='migration',
        ),
        migrations.DeleteModel(
            name='MigrationStep',
        ),
    ]
