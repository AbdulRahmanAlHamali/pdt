# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import post_office.fields
import post_office.validators


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0002_add_i18n_and_backend_alias'),
        ('core', '0038_auto_20151020_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('from_email', models.CharField(validators=[post_office.validators.validate_email_with_name], verbose_name='Email From', max_length=254)),
                ('to', post_office.fields.CommaSeparatedEmailField(verbose_name='Email To', blank=True)),
                ('cc', post_office.fields.CommaSeparatedEmailField(verbose_name='Cc', blank=True)),
                ('bcc', post_office.fields.CommaSeparatedEmailField(verbose_name='Bcc', blank=True)),
                ('subject', models.CharField(verbose_name='Subject', blank=True, max_length=255)),
                ('template', models.ForeignKey(to='post_office.EmailTemplate')),
            ],
        ),
        migrations.AddField(
            model_name='instance',
            name='notification_template',
            field=models.ForeignKey(null=True, blank=True, to='core.NotificationTemplate'),
        ),
    ]
