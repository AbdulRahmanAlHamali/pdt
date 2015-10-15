# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20151015_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploymentreport',
            name='cases',
            field=models.ManyToManyField(to='core.Case'),
        ),
    ]
