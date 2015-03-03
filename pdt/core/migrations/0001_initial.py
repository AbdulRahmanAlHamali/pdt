# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
                ('project', models.CharField(max_length=255, blank=True)),
                ('area', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CIProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeploymentReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('status', models.CharField(max_length=3, choices=[('dpl', 'Deployed'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Migration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('category', models.CharField(default='onl', max_length=3, choices=[('off', 'Offline'), ('onl', 'Online')])),
                ('sql', models.TextField(blank=True)),
                ('code', models.TextField(blank=True)),
                ('case', models.OneToOneField(to='core.Case')),
            ],
        ),
        migrations.CreateModel(
            name='MigrationReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('status', models.CharField(max_length=3, choices=[('apl', 'Applied'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField(blank=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
                ('migration', models.ForeignKey(to='core.Migration')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('date', models.DateField()),
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
    ]
