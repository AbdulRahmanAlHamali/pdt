# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20151016_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deploymentreport',
            name='cases',
            field=models.ManyToManyField(to='core.Case', related_name='deployment_reports'),
        ),
    ]
