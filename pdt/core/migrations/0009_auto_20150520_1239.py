# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_caseedit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseedit',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True),
        ),
    ]
