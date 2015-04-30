# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150430_1400'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deploymentreport',
            options={'ordering': ['release', 'instance', 'datetime']},
        ),
        migrations.AlterModelOptions(
            name='migrationreport',
            options={'ordering': ['migration', 'instance', 'datetime']},
        ),
        migrations.AlterModelOptions(
            name='migrationstepreport',
            options={'ordering': ['report', 'step', 'datetime']},
        ),
        migrations.AlterField(
            model_name='migrationreport',
            name='migration',
            field=models.ForeignKey(to='core.Migration', related_name='reports'),
        ),
        migrations.AlterField(
            model_name='migrationstepreport',
            name='report',
            field=models.ForeignKey(to='core.MigrationReport', related_name='step_reports'),
        ),
    ]
