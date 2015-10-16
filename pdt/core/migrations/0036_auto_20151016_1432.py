# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20151016_0929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instance',
            options={'ordering': ['name', 'id'], 'verbose_name': 'Instance', 'verbose_name_plural': 'Instances'},
        ),
        migrations.AddField(
            model_name='instance',
            name='ci_projects',
            field=models.ManyToManyField(to='core.CIProject', verbose_name='CI projects', related_name='instances'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='instance',
            name='ci_project',
        ),
    ]
