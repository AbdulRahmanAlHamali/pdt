# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150502_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='name',
            field=models.PositiveIntegerField(unique=True, db_index=True),
        ),
    ]
