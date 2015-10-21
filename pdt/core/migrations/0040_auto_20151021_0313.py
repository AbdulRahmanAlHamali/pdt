# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import post_office.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20151021_0300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationtemplate',
            name='subject',
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='bcc',
            field=post_office.fields.CommaSeparatedEmailField(blank=True, verbose_name='Bcc', null=True),
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='cc',
            field=post_office.fields.CommaSeparatedEmailField(blank=True, verbose_name='Cc', null=True),
        ),
    ]
