# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150527_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deploymentreport',
            name='status',
            field=models.CharField(choices=[('dpl', 'Deployed'), ('err', 'Error')], max_length=3),
        ),
    ]
