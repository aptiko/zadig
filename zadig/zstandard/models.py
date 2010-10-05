from django.db import models
from zadig.core import models as coremodels

class EntryOptions(models.Model):
    entry = models.OneToOneField(coremodels.Entry, primary_key=True)
    no_navigation = models.BooleanField()
    no_breadcrumbs = models.BooleanField()
    navigation_toplevel = models.BooleanField()
    class Meta:
        db_table = 'zstandard_entryoptions'
