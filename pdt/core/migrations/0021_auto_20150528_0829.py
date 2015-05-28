# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_casecategory_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', blank=True, to='taggit.Tag', verbose_name='Tags', through='taggit.TaggedItem'),
        ),
        migrations.AlterField(
            model_name='casecategory',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', blank=True, to='taggit.Tag', verbose_name='Tags', through='taggit.TaggedItem'),
        ),
    ]
