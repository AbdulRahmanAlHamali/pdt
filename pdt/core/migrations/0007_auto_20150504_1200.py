# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_case_modified_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='migrationreport',
            name='datetime',
            field=models.DateTimeField(db_index=True, auto_now=True),
        ),
    ]
