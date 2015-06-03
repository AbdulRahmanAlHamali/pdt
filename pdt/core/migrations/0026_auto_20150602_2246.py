# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20150530_2100'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalMigrationStep',
            fields=[
                ('migrationstep_ptr', models.OneToOneField(to='core.MigrationStep', primary_key=True, parent_link=True, auto_created=True, serialize=False)),
            ],
            bases=('core.migrationstep',),
        ),
        migrations.AddField(
            model_name='migration',
            name='parent',
            field=models.ForeignKey(null=True, to='core.Migration', blank=True),
        ),
        migrations.AddField(
            model_name='finalmigrationstep',
            name='migration',
            field=models.ForeignKey(related_name='final_steps', to='core.Migration'),
        ),
    ]
