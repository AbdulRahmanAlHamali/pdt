# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import post_office.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20151021_0313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='bcc',
            field=post_office.fields.CommaSeparatedEmailField(verbose_name='Bcc', default=[], blank=True),
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='cc',
            field=post_office.fields.CommaSeparatedEmailField(verbose_name='Cc', default=[], blank=True),
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='to',
            field=post_office.fields.CommaSeparatedEmailField(verbose_name='Email To', default=[], blank=True),
        ),
    ]
