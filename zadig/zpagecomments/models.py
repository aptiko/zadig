from django.db import models
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.template import RequestContext
from django.template.loader import render_to_string

from zadig.core import entry_option_sets
from zadig.core.models import Entry, PERM_VIEW, PERM_EDIT
from zadig.zstandard.models import PageEntry

STATE_UNAPPROVED = u'UNAPPROVED'
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
    comment_source = models.TextField()
    comment_html = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    state = CommentStateField()

    def __unicode__(self):
        return u'Comment id=%s on page id=%s' % (self.id, self.page.id)

    @property
    def state_name(self):
        return { STATE_DELETED: _(u"deleted"), STATE_PUBLISHED: _(u"published"),
                 STATE_UNAPPROVED: _(u"unapproved") }[self.state]

    @property
    def linked_commenter_name(self):
        name = escape(self.commenter_name)
        return mark_safe('<a href="%s">%s</a>' % (escape(self.commenter_website),
            name) if self.commenter_website else name)

    def render(self, request):
        entry = self.page
        entry.request = request
        p = entry.permissions
        if PERM_VIEW not in p: return ''
        if self.state != STATE_PUBLISHED and PERM_EDIT not in p:
            return ''
        self.visible_commenter_email = mark_safe('' if PERM_EDIT not in p else ('&lt;' +
                                                escape(self.commenter_email) + '&gt;'))
        return render_to_string("show_comment.html", context_instance=RequestContext(
                            request, { "comment": self, "perm_edit": PERM_EDIT in p }))


class CommentForm(forms.Form):
    comment_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    commenter_name = forms.CharField(max_length=100, required=True,
                                label=_(u'Name'))
    commenter_email = forms.EmailField(required=True, label=_(u'Email'))
    commenter_website = forms.URLField(required=False, label=_(u'Website'))
    comment = forms.CharField(label='', required=True, widget=forms.Textarea)
    comment_state = forms.CharField(widget=forms.HiddenInput(),
                                                initial=STATE_PUBLISHED)


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
