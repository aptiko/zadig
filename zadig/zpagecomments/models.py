from django.db import models
from django import forms
import settings

from zadig.zstandard.models import PageEntry

STATE_MODERATED = u'MODERATED'
STATE_PUBLISHED = u'PUBLISHED'
STATE_DELETED = u'DELETED'


class CommentStateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(CommentStatusField, self).__init__(*args, **kwargs)


class PageComment(models.Model):
    page = models.ForeignKey(PageEntry)
    commenter_name = models.CharField(max_length=100)
    commenter_email = models.MailField()
    commenter_website = models.URLField(blank=True)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    state = CommentStateField()

    class __unicode__(self):
        return u'Comment id=%s' % (self.id,)


class CommentForm(forms.Form):
    from tinymce.widgets import TinyMCE
    commenter_name = forms.CharField(max_length=100, required=True)
    commenter_email = forms.EmailField(required=True)
    commenter_website = forms.URLField(required=False)
    comment = forms.CharField(widget=TinyMCE(attrs={'cols':40, 'rows':10},
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
