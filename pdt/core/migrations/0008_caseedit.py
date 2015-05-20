# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150504_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseEdit',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=10, choices=[('migration-url', 'Migration URL')])),
                ('case', models.ForeignKey(related_name='edits', to='core.Case')),
            ],
        ),
    ]
