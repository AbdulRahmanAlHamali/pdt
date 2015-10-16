# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_deploymentreport_cases'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploymentreport',
            name='revision',
            field=models.CharField(db_index=True, max_length=255, blank=True),
        ),
        migrations.AlterIndexTogether(
            name='deploymentreport',
            index_together=set([('release', 'instance', 'datetime', 'id', 'revision')]),
        ),
    ]
