# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150528_0826'),
    ]

    operations = [
        migrations.AddField(
            model_name='casecategory',
            name='title',
            field=models.CharField(max_length=255, default='', db_index=True),
            preserve_default=False,
        ),
    ]
