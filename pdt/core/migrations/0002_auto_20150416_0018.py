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
            name='MigrationStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(choices=[('sql', 'SQL'), ('python', 'Python')], max_length=10)),
                ('code', models.TextField()),
                ('path', models.CharField(blank=True, max_length=255)),
            ],
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
            model_name='migrationstep',
            name='migration',
            field=models.ForeignKey(to='core.Migration'),
        ),
    ]
