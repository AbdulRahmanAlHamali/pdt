# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20150529_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deploymentreport',
            name='instance',
            field=models.ForeignKey(to='core.Instance', related_name='deployment_reports'),
        ),
        migrations.AlterField(
            model_name='deploymentreport',
            name='release',
            field=models.ForeignKey(to='core.Release', related_name='deployment_reports'),
        ),
    ]
