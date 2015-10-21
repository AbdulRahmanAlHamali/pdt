# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20151020_1602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deploymentreport',
            options={'verbose_name': 'Deployment report', 'verbose_name_plural': 'Deployment reports', 'ordering': ['instance', 'datetime', 'id']},
        ),
        migrations.AlterIndexTogether(
            name='deploymentreport',
            index_together=set([('instance', 'datetime', 'id')]),
        ),
        migrations.RemoveField(
            model_name='deploymentreport',
            name='release',
        ),
        migrations.RemoveField(
            model_name='deploymentreport',
            name='revision',
        ),
    ]
