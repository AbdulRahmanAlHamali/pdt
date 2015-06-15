# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20150615_1347'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ciproject',
            options={'ordering': ['name', 'id'], 'verbose_name_plural': 'CI projects', 'verbose_name': 'CI project'},
        ),
        migrations.AlterModelOptions(
            name='instance',
            options={'ordering': ['name', 'ci_project', 'id'], 'verbose_name_plural': 'Instances', 'verbose_name': 'Instance'},
        ),
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ['number', 'id'], 'verbose_name_plural': 'Releases', 'verbose_name': 'Release'},
        ),
    ]
