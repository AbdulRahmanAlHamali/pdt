# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20150609_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='ci_project',
            field=models.ForeignKey(to='core.CIProject', related_name='cases'),
        ),
    ]
