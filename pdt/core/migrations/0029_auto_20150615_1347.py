# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20150610_1428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ciproject',
            options={'verbose_name_plural': 'CI projects', 'verbose_name': 'CI project', 'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='instance',
            options={'verbose_name_plural': 'Instances', 'verbose_name': 'Instance', 'ordering': ['name', 'ci_project']},
        ),
        migrations.AlterModelOptions(
            name='release',
            options={'verbose_name_plural': 'Releases', 'verbose_name': 'Release', 'ordering': ['number']},
        ),
        migrations.AlterField(
            model_name='migrationreport',
            name='instance',
            field=models.ForeignKey(to='core.Instance', related_name='migration_reports'),
        ),
    ]
