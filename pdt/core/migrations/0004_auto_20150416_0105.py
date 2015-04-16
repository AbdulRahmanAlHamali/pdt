# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150416_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='migrationstep',
            name='path',
            field=models.CharField(null=True, blank=True, max_length=255),
        ),
    ]
