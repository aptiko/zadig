# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryOptionSet',
            fields=[
                ('entry', models.OneToOneField(related_name='ZstandardEntryOptions', primary_key=True, serialize=False, to='core.Entry')),
                ('no_navigation', models.BooleanField(default=False)),
                ('no_breadcrumbs', models.BooleanField(default=False)),
                ('navigation_toplevel', models.BooleanField(default=False)),
                ('show_author', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'zstandard_entryoptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Entry')),
            ],
            options={
            },
            bases=('core.entry',),
        ),
        migrations.CreateModel(
            name='ImageEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Entry')),
            ],
            options={
            },
            bases=('core.entry',),
        ),
        migrations.CreateModel(
            name='InternalRedirectionEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Entry')),
            ],
            options={
            },
            bases=('core.entry',),
        ),
        migrations.CreateModel(
            name='LinkEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Entry')),
            ],
            options={
            },
            bases=('core.entry',),
        ),
        migrations.CreateModel(
            name='PageEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Entry')),
            ],
            options={
            },
            bases=('core.entry',),
        ),
        migrations.CreateModel(
            name='NewsItemEntry',
            fields=[
                ('pageentry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='zstandard.PageEntry')),
            ],
            options={
            },
            bases=('zstandard.pageentry',),
        ),
        migrations.CreateModel(
            name='EventEntry',
            fields=[
                ('pageentry_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='zstandard.PageEntry')),
            ],
            options={
            },
            bases=('zstandard.pageentry',),
        ),
        migrations.CreateModel(
            name='VFile',
            fields=[
                ('vobject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.VObject')),
                ('content', models.FileField(null=True, upload_to=b'files', blank=True)),
            ],
            options={
            },
            bases=('core.vobject',),
        ),
        migrations.CreateModel(
            name='VImage',
            fields=[
                ('vobject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.VObject')),
                ('content', models.ImageField(null=True, upload_to=b'images', blank=True)),
            ],
            options={
            },
            bases=('core.vobject',),
        ),
        migrations.CreateModel(
            name='VInternalRedirection',
            fields=[
                ('vobject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.VObject')),
                ('target', models.ForeignKey(to='core.Entry')),
            ],
            options={
            },
            bases=('core.vobject',),
        ),
        migrations.CreateModel(
            name='VLink',
            fields=[
                ('vobject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.VObject')),
                ('target', models.URLField(blank=True)),
            ],
            options={
            },
            bases=('core.vobject',),
        ),
        migrations.CreateModel(
            name='VPage',
            fields=[
                ('vobject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.VObject')),
                ('content', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('core.vobject',),
        ),
        migrations.CreateModel(
            name='VNewsItem',
            fields=[
                ('vpage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='zstandard.VPage')),
                ('news_date', models.DateTimeField(db_index=True)),
            ],
            options={
            },
            bases=('zstandard.vpage',),
        ),
        migrations.CreateModel(
            name='VEvent',
            fields=[
                ('vpage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='zstandard.VPage')),
                ('event_start', models.DateTimeField(db_index=True)),
                ('event_end', models.DateTimeField(db_index=True)),
            ],
            options={
            },
            bases=('zstandard.vpage',),
        ),
    ]
