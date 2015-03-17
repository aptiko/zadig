# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.db import migrations


def create_root_page(apps, schema_editor):
    PageEntry = apps.get_model('zstandard', 'PageEntry')
    State = apps.get_model('core', 'State')
    VPage = apps.get_model('zstandard', 'VPage')
    VObjectMetatags = apps.get_model('core', 'VObjectMetatags')
    entry = PageEntry(container=None, name='', seq=1, owner_id=1,
                      state=State.objects.get(descr="Published"))
    entry.save()
    page = VPage(object_class='VPage', entry=entry, version_number=1,
                 language_id=settings.ZADIG_LANGUAGES[0][0],
                 content='This is the root page',
                 date=datetime.now())
    page.save()
    entry.vobject = page
    entry.save()
    nmetatags = VObjectMetatags(
        vobject=page, language_id=settings.ZADIG_LANGUAGES[0][0],
        title='Welcome', short_title='Home', description='Root page.')
    nmetatags.save()


class Migration(migrations.Migration):

    dependencies = [
        ('zstandard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_root_page),
    ]
