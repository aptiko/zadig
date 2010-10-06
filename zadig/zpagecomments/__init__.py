from django import forms
from django.utils.translation import ugettext as _
from zadig.zpagecomments import models
from zadig.zstandard.models import PageEntry

class EntryOptionsForm(forms.Form):
    # TODO: A problem occurs (at least in syncdb) if the labels below are
    # translatable strings, therefore they are temporarily untranslatable
    allow_comments = forms.BooleanField(label=u"Allow comments",
                                                    required=False)

def entry_options(entry, form=None):
    if not isinstance(entry.descendant, PageEntry):
        return None
    try:
        entryoptions = models.EntryOptions.objects.get(entry=entry)
    except models.EntryOptions.DoesNotExist:
        entryoptions = models.EntryOptions(entry=entry, allow_comments=False)
    if not form:
        form = EntryOptionsForm({'allow_comments': entryoptions.allow_comments,
            })
        return form
    else:
        entryoptions.allow_comments = form.cleaned_data['allow_comments']
        entryoptions.save()
