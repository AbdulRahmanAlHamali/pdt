# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_case_revision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='revision',
            field=models.CharField(db_index=True, max_length=255, blank=True),
        ),
        migrations.AlterIndexTogether(
            name='case',
            index_together=set([('ci_project', 'release'), ('id', 'title', 'revision')]),
        ),
    ]
