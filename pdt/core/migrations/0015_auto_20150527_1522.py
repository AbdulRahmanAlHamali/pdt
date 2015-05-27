# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150527_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='release',
            field=models.ForeignKey(to='core.Release', related_name='cases', blank=True, null=True),
        ),
    ]
