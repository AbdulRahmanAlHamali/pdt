# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20150615_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='ci_project',
            field=models.ForeignKey(verbose_name='CI project', related_name='cases', to='core.CIProject'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='ci_project',
            field=models.ForeignKey(verbose_name='CI project', related_name='instances', to='core.CIProject'),
        ),
        migrations.AlterField(
            model_name='migrationstepreport',
            name='step',
            field=models.ForeignKey(to='core.MigrationStep', related_name='reports'),
        ),
    ]
