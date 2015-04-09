# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('project', models.CharField(blank=True, max_length=255)),
                ('area', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CIProject',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DeploymentReport',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status', models.CharField(choices=[('dpl', 'Deployed'), ('err', 'Error')], max_length=3)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('ci_project', models.ForeignKey(to='core.CIProject')),
            ],
        ),
        migrations.CreateModel(
            name='Migration',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('uid', models.CharField(unique=True, max_length=255)),
                ('category', models.CharField(choices=[('off', 'Offline'), ('onl', 'Online')], max_length=3, default='onl')),
                ('sql', models.TextField(blank=True)),
                ('code', models.TextField(blank=True)),
                ('case', models.OneToOneField(to='core.Case')),
            ],
        ),
        migrations.CreateModel(
            name='MigrationReport',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status', models.CharField(choices=[('apl', 'Applied'), ('err', 'Error')], max_length=3)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField(blank=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
                ('migration', models.ForeignKey(to='core.Migration')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('datetime', models.DateTimeField(default=datetime.date.today)),
            ],
        ),
        migrations.AddField(
            model_name='deploymentreport',
            name='instance',
            field=models.ForeignKey(to='core.Instance'),
        ),
        migrations.AddField(
            model_name='deploymentreport',
            name='release',
            field=models.ForeignKey(to='core.Release'),
        ),
        migrations.AddField(
            model_name='case',
            name='ci_project',
            field=models.ForeignKey(to='core.CIProject'),
        ),
        migrations.AddField(
            model_name='case',
            name='release',
            field=models.ForeignKey(to='core.Release'),
        ),
        migrations.AlterUniqueTogether(
            name='migrationreport',
            unique_together=set([('migration', 'instance')]),
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([('name', 'ci_project')]),
        ),
    ]
