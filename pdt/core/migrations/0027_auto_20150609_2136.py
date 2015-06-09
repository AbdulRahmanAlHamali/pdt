# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20150602_2246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='case',
            options={'verbose_name': 'Case', 'verbose_name_plural': 'Cases'},
        ),
        migrations.AlterModelOptions(
            name='casecategory',
            options={'verbose_name': 'Case category', 'ordering': ['position'], 'verbose_name_plural': 'Case categories'},
        ),
        migrations.AlterModelOptions(
            name='caseedit',
            options={'verbose_name': 'Case edit', 'verbose_name_plural': 'Case edits'},
        ),
        migrations.AlterModelOptions(
            name='ciproject',
            options={'verbose_name': 'CI project', 'verbose_name_plural': 'CI projects'},
        ),
        migrations.AlterModelOptions(
            name='deploymentreport',
            options={'verbose_name': 'Deployment report', 'ordering': ['release', 'instance', 'datetime', 'id'], 'verbose_name_plural': 'Deployment reports'},
        ),
        migrations.AlterModelOptions(
            name='finalmigrationstep',
            options={'verbose_name': 'Final migration step', 'verbose_name_plural': 'Final migration steps'},
        ),
        migrations.AlterModelOptions(
            name='instance',
            options={'verbose_name': 'Instance', 'verbose_name_plural': 'Instances'},
        ),
        migrations.AlterModelOptions(
            name='migration',
            options={'verbose_name': 'Migration', 'verbose_name_plural': 'Migrations'},
        ),
        migrations.AlterModelOptions(
            name='migrationreport',
            options={'ordering': ['migration', 'instance', 'datetime', 'id'], 'verbose_name': 'Migration report', 'verbose_name_plural': 'Migration reports'},
        ),
        migrations.AlterModelOptions(
            name='migrationstep',
            options={'verbose_name': 'Migration step', 'ordering': ['position'], 'verbose_name_plural': 'Migration steps'},
        ),
        migrations.AlterModelOptions(
            name='migrationstepreport',
            options={'ordering': ['report', 'step', 'datetime', 'id'], 'verbose_name': 'Migration step report', 'verbose_name_plural': 'Migration step reports'},
        ),
        migrations.AlterModelOptions(
            name='postdeploymigrationstep',
            options={'verbose_name': 'Post-deploy migration step', 'verbose_name_plural': 'Post-deploy migration steps'},
        ),
        migrations.AlterModelOptions(
            name='predeploymigrationstep',
            options={'verbose_name': 'Pre-deploy migration step', 'verbose_name_plural': 'Pre-deploy migration steps'},
        ),
        migrations.AlterModelOptions(
            name='release',
            options={'verbose_name': 'Release', 'verbose_name_plural': 'Releases'},
        ),
    ]
