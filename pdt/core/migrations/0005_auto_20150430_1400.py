# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_migration_reviewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrationStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(max_length=10, choices=[('mysql', 'MySQL'), ('pgsql', 'pgSQL'), ('python', 'Python'), ('sh', 'Shell')])),
                ('code', models.TextField()),
                ('path', models.CharField(null=True, max_length=255, blank=True)),
                ('position', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='MigrationStepReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('status', models.CharField(max_length=3, choices=[('apl', 'Applied'), ('err', 'Error')])),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('log', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='postdeploymigrationstep',
            options={},
        ),
        migrations.AlterModelOptions(
            name='predeploymigrationstep',
            options={},
        ),
        migrations.RemoveField(
            model_name='postdeploymigrationstep',
            name='code',
        ),
        migrations.RemoveField(
            model_name='postdeploymigrationstep',
            name='id',
        ),
        migrations.RemoveField(
            model_name='postdeploymigrationstep',
            name='path',
        ),
        migrations.RemoveField(
            model_name='postdeploymigrationstep',
            name='position',
        ),
        migrations.RemoveField(
            model_name='postdeploymigrationstep',
            name='type',
        ),
        migrations.RemoveField(
            model_name='predeploymigrationstep',
            name='code',
        ),
        migrations.RemoveField(
            model_name='predeploymigrationstep',
            name='id',
        ),
        migrations.RemoveField(
            model_name='predeploymigrationstep',
            name='path',
        ),
        migrations.RemoveField(
            model_name='predeploymigrationstep',
            name='position',
        ),
        migrations.RemoveField(
            model_name='predeploymigrationstep',
            name='type',
        ),
        migrations.AlterField(
            model_name='migrationreport',
            name='status',
            field=models.CharField(max_length=3, choices=[('apl', 'Applied'), ('prt', 'Applied partially'), ('err', 'Error')]),
        ),
        migrations.AddField(
            model_name='migrationstepreport',
            name='report',
            field=models.ForeignKey(to='core.MigrationReport'),
        ),
        migrations.AddField(
            model_name='migrationstepreport',
            name='step',
            field=models.ForeignKey(to='core.MigrationStep'),
        ),
        migrations.AddField(
            model_name='postdeploymigrationstep',
            name='migrationstep_ptr',
            field=models.OneToOneField(primary_key=True, serialize=False, to='core.MigrationStep', default=None, parent_link=True, auto_created=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='predeploymigrationstep',
            name='migrationstep_ptr',
            field=models.OneToOneField(primary_key=True, serialize=False, to='core.MigrationStep', default=1, parent_link=True, auto_created=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='migrationstepreport',
            unique_together=set([('report', 'step')]),
        ),
    ]
