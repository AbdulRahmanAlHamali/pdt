# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150501_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='release',
            field=models.ForeignKey(null=True, to='core.Release', blank=True),
        ),
    ]
