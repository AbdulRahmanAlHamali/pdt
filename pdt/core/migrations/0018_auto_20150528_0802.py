# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('core', '0017_case_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', verbose_name='Tags', to='taggit.Tag', through='taggit.TaggedItem')),
            ],
        ),
        migrations.RemoveField(
            model_name='case',
            name='tags'
        ),
        migrations.AddField(
            model_name='case',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', verbose_name='Tags', to='taggit.Tag', through='taggit.TaggedItem'),
        ),
    ]
