# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20150527_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='tags',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
