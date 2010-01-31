from django import forms
from django.utils.translation import ugettext as _
from cms.core import models as coremodels
from cms.applets.standard import models

class EntryOptionsForm(forms.Form):
    # TODO: A problem occurs (at least in syncdb) if the label below is a
    # translatable string, therefore it is temporarily untranslatable
    no_navigation = forms.BooleanField(label=u"Don't show in Navigation",
                                                    required=False)

def entry_options(request, site, path, form=None):
    entry = coremodels.Entry.objects.get_by_path(request, site, path)
    try:
        entryoptions = models.EntryOptions.objects.get(entry=entry)
    except models.EntryOptions.DoesNotExist:
        entryoptions = models.EntryOptions(entry=entry, no_navigation=False)
    if not form:
        form = EntryOptionsForm({'no_navigation': entryoptions.no_navigation })
        return form
    else:
        entryoptions.no_navigation = form.cleaned_data['no_navigation']
        entryoptions.save()
