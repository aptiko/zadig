from django.http import Http404

from zadig.core.models import Entry
from zadig.zstandard.models import PageEntry
from zadig.zpagecomments.models import EntryOptions, PageComment, CommentForm, \
                                        STATE_PUBLISHED

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
    else:
        vobject.request.pagecommentsform = form
    return vobject.end_view()
