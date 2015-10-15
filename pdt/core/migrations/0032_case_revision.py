# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20150618_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='revision',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
