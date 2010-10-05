from django import forms
from django.utils.translation import ugettext as _
from zadig.core import models as coremodels
from zadig.zstandard import models

class EntryOptionsForm(forms.Form):
    # TODO: A problem occurs (at least in syncdb) if the labels below are
    # translatable strings, therefore they are temporarily untranslatable
    no_breadcrumbs = forms.BooleanField(label=u"Don't show in Breadcrumbs",
                                                    required=False)
    no_navigation = forms.BooleanField(label=u"Don't show in Navigation",
                                                    required=False)
    navigation_toplevel = forms.BooleanField(required=False,
                        label=u"Show this page as top level in navigation")

def entry_options(entry, form=None):
    try:
        entryoptions = models.EntryOptions.objects.get(entry=entry)
    except models.EntryOptions.DoesNotExist:
        entryoptions = models.EntryOptions(entry=entry, no_breadcrumbs=False,
            no_navigation=False, navigation_toplevel=False)
    if not form:
        form = EntryOptionsForm({'no_breadcrumbs': entryoptions.no_breadcrumbs,
            'no_navigation': entryoptions.no_navigation,
            'navigation_toplevel': entryoptions.navigation_toplevel})
        return form
    else:
        entryoptions.no_breadcrumbs = form.cleaned_data['no_breadcrumbs']
        entryoptions.no_navigation = form.cleaned_data['no_navigation']
        entryoptions.navigation_toplevel = form.cleaned_data[
                                                        'navigation_toplevel']
        entryoptions.save()

portlets = [
    { 'name': _(u"Navigation"),
      'tag': 'navigation', },
]
