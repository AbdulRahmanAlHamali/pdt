# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150502_1913'),
    ]

    operations = [
        migrations.RenameField(
            model_name='release',
            old_name='name',
            new_name='number',
        ),
    ]
