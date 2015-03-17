# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_class', models.CharField(max_length=100)),
                ('name', models.SlugField(max_length=100, blank=True)),
                ('seq', models.PositiveIntegerField()),
                ('btemplate', models.CharField(max_length=100, blank=True)),
                ('container', models.ForeignKey(related_name='all_subentries', blank=True, to='core.Entry', null=True)),
            ],
            options={
                'ordering': ('container__id', 'seq'),
                'db_table': 'zadig_entry',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntryPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry', models.ForeignKey(to='core.Entry')),
            ],
            options={
                'db_table': 'zadig_entrypermission',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('descr', models.CharField(max_length=63)),
            ],
            options={
                'db_table': 'zadig_language',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lentity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('special', models.PositiveSmallIntegerField(null=True)),
                ('group', models.ForeignKey(to='auth.Group', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'zadig_lentity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultilingualGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'zadig_multilingualgroup',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descr', models.CharField(max_length=31)),
            ],
            options={
                'db_table': 'zadig_permission',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descr', models.CharField(max_length=31)),
            ],
            options={
                'db_table': 'zadig_state',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatePermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lentity', models.ForeignKey(to='core.Lentity')),
                ('permission', models.ForeignKey(to='core.Permission')),
                ('state', models.ForeignKey(to='core.State')),
            ],
            options={
                'db_table': 'zadig_statepermission',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StateTransition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lentity', models.ForeignKey(to='core.Lentity')),
                ('source_state', models.ForeignKey(related_name='source_rules', to='core.State')),
                ('target_state', models.ForeignKey(related_name='target_rules', to='core.State')),
            ],
            options={
                'db_table': 'zadig_statetransition',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_class', models.CharField(max_length=100)),
                ('version_number', models.PositiveIntegerField()),
                ('date', models.DateTimeField()),
                ('deletion_mark', models.BooleanField(default=False)),
                ('entry', models.ForeignKey(related_name='vobject_set', to='core.Entry')),
                ('language', models.ForeignKey(blank=True, to='core.Language', null=True)),
            ],
            options={
                'ordering': ('entry', 'version_number'),
                'db_table': 'zadig_vobject',
                'permissions': (('view', 'View'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VObjectMetatags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('short_title', models.CharField(max_length=250, blank=True)),
                ('description', models.TextField(blank=True)),
                ('language', models.ForeignKey(to='core.Language')),
                ('vobject', models.ForeignKey(related_name='metatags', to='core.VObject')),
            ],
            options={
                'db_table': 'zadig_vobjectmetatags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=127)),
                ('state_transitions', models.ManyToManyField(to='core.StateTransition')),
                ('states', models.ManyToManyField(to='core.State')),
            ],
            options={
                'db_table': 'zadig_workflow',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vobjectmetatags',
            unique_together=set([('vobject', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='vobject',
            unique_together=set([('entry', 'version_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='lentity',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AddField(
            model_name='entrypermission',
            name='lentity',
            field=models.ForeignKey(to='core.Lentity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entrypermission',
            name='permission',
            field=models.ForeignKey(to='core.Permission'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entrypermission',
            unique_together=set([('lentity', 'permission')]),
        ),
        migrations.AddField(
            model_name='entry',
            name='multilingual_group',
            field=models.ForeignKey(blank=True, to='core.MultilingualGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='state',
            field=models.ForeignKey(to='core.State'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='vobject',
            field=models.OneToOneField(related_name='irrelevant', null=True, to='core.VObject'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('container', 'name'), ('container', 'seq')]),
        ),
    ]
