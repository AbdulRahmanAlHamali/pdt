# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150416_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='migration',
            name='post_steps',
            field=models.ManyToManyField(to='core.MigrationStep', related_name='migration_post_steps'),
        ),
        migrations.AddField(
            model_name='migration',
            name='pre_steps',
            field=models.ManyToManyField(to='core.MigrationStep', related_name='migration_pre_steps'),
        ),
    ]
