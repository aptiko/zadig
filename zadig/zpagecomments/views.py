from django.http import Http404
from django.utils.translation import ugettext as _

from zadig.core.models import Entry
from zadig.zstandard.models import PageEntry
from zadig.zpagecomments.models import PageComment, CommentForm, STATE_PUBLISHED

def add_comment(vobject, parms=None):
    entry = vobject.rentry.descendant
    if vobject.request.method != 'POST' or not isinstance(entry, PageEntry):
        raise Http404
    try:
        if not entry.ZpagecommentsEntryOptions.allow_comments: raise Http404
    except EntryOptions.DoesNotExist:
        raise Http404
    form = CommentForm(vobject.request.POST)
    if form.is_valid():
        comment = PageComment(
            page=entry,
            commenter_name=form.cleaned_data['commenter_name'],
            commenter_email=form.cleaned_data['commenter_email'],
            commenter_website=form.cleaned_data['commenter_website'],
            comment=form.cleaned_data['comment'],
            state=STATE_PUBLISHED)
        comment.save()
        vobject.request.message = _(u"Your comment has been added.")
    else:
        vobject.request.pagecommentsform = form
        vobject.request.message = _(
                    u"There was an error in your comment; see below.")
    return vobject.end_view()
