from django.db import models
from twistycms.core import models as coremodels

class EntryOptions(models.Model):
    entry = models.OneToOneField(coremodels.Entry, primary_key=True)
    no_navigation = models.BooleanField()
    no_breadcrumbs = models.BooleanField()
    navigation_toplevel = models.BooleanField()
