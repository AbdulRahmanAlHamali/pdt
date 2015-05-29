# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_release_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ciproject',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='instance',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
