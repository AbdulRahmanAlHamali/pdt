# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150417_0301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postdeploymigrationstep',
            name='type',
            field=models.CharField(choices=[('mysql', 'MySQL'), ('pgsql', 'pgSQL'), ('python', 'Python'), ('sh', 'Shell')], max_length=10),
        ),
        migrations.AlterField(
            model_name='predeploymigrationstep',
            name='type',
            field=models.CharField(choices=[('mysql', 'MySQL'), ('pgsql', 'pgSQL'), ('python', 'Python'), ('sh', 'Shell')], max_length=10),
        ),
    ]
