# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150527_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseedit',
            name='type',
            field=models.CharField(choices=[('migration-url', 'Migration URL'), ('migration-reviewed', 'Migration reviewed'), ('migration-unreviewed', 'Migration unreviewed'), ('migration-report', 'Migration report'), ('deployment-report', 'Deployment report')], max_length=50),
        ),
    ]
