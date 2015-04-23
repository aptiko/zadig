# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from zadig.core.models import State, VObjectMetatags
from zadig.zstandard.models import PageEntry, VPage


class Command(BaseCommand):
    help = 'Creates the root page'

    @transaction.atomic
    def handle(self, *args, **options):
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
