# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20150528_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='casecategory',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='casecategory',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
