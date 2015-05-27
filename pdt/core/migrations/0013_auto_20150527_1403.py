# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_caseedit_params'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseedit',
            name='type',
            field=models.CharField(max_length=50, choices=[('migration-url', 'Migration URL'), ('migration-reviewed', 'Migration reviewed'), ('migration-unreviewed', 'Migration unreviewed'), ('migration-report', 'Migration report')]),
        ),
        migrations.AlterField(
            model_name='deploymentreport',
            name='status',
            field=models.CharField(max_length=3, choices=[('apl', 'Applied'), ('err', 'Error')]),
        ),
    ]
