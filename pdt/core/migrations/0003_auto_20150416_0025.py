# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150416_0018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='migrationstep',
            options={'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='migrationstep',
            name='position',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
