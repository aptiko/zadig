from django.db import models
from django import forms
from django.utils.translation import ugettext as _
import settings

from zadig.core import entry_option_sets
from zadig.core.models import Entry
from zadig.zstandard.models import PageEntry

STATE_MODERATED = u'MODERATED'
STATE_PUBLISHED = u'PUBLISHED'
STATE_DELETED = u'DELETED'


class CommentStateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(CommentStateField, self).__init__(*args, **kwargs)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], [r"^zadig.zpagecomments.models.CommentStateField"])


class PageComment(models.Model):
    page = models.ForeignKey(PageEntry)
    commenter_name = models.CharField(max_length=100)
    commenter_email = models.EmailField()
    commenter_website = models.URLField(blank=True)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    state = CommentStateField()

    def __unicode__(self):
        return u'Comment id=%s' % (self.id,)


class CommentForm(forms.Form):
    from tinymce.widgets import TinyMCE
    commenter_name = forms.CharField(max_length=100, required=True,
                                label=_(u'Name'))
    commenter_email = forms.EmailField(required=True, label=_(u'Email'))
    commenter_website = forms.URLField(required=False, label=_(u'Website'))
    comment = forms.CharField(label='',
        widget=TinyMCE(attrs={'cols':40, 'rows':10},
        mce_attrs={
            'content_css': settings.ZADIG_MEDIA_URL + '/style.css',
            'convert_urls': True,
            'entity_encoding': 'raw',
            'theme': 'advanced',
            'plugins': 'table,inlinepopups,autosave',
            'theme_advanced_blockformats': settings.ZADIG_TINYMCE_BLOCKFORMATS,
            'theme_advanced_styles': settings.ZADIG_TINYMCE_STYLES,
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_toolbar_align': 'left',
            'theme_advanced_buttons1': 'bold,italic,sup,sub,|,numlist,bullist,outdent,indent,|,link,unlink,|,removeformat,code,formatselect,styleselect',
            'theme_advanced_buttons2': '',
            'theme_advanced_buttons3': '',
            'popup_css': settings.ZADIG_MEDIA_URL + '/tinymce_popup.css',
        }), required=True)

    def clean_comment(self):
        from zadig.core.utils import sanitize_html
        result = sanitize_html( self.cleaned_data['comment'])
        if not result:
            raise forms.ValidationError(_(
                        u"Don't try to be too clever with the HTML."))
        return result


class EntryOptionsForm(forms.Form):
    allow_comments = forms.BooleanField(label=_(u"Allow comments"),
                                                    required=False)


class EntryOptionSet(models.Model):
    entry = models.OneToOneField(Entry, primary_key=True,
                                related_name="ZpagecommentsEntryOptions")
    allow_comments = models.BooleanField()

    form = EntryOptionsForm

    def get_form_from_data(self):
        if not isinstance(self.entry.descendant, PageEntry): return None
        return EntryOptionsForm({'allow_comments': self.allow_comments, })

    def set_data_from_form(self, form):
        self.allow_comments = form.cleaned_data['allow_comments']

    class Meta:
        db_table = 'zpagecomments_entryoptions'


entry_option_sets.append(EntryOptionSet)
