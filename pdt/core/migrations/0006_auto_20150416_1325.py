# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150416_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='migration',
            name='post_steps',
        ),
        migrations.RemoveField(
            model_name='migration',
            name='pre_steps',
        ),
    ]
