# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150528_0802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='casecategory',
            options={'verbose_name_plural': 'Case categories', 'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='casecategory',
            name='position',
            field=models.PositiveSmallIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterIndexTogether(
            name='casecategory',
            index_together=set([('id', 'position')]),
        ),
    ]
