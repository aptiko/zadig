from django.http import Http404
from django.utils.translation import ugettext as _

from zadig.core.models import Entry, permissions
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
        from docutils.core import publish_parts
        from zadig.core.utils import sanitize_html
        parts = publish_parts(source=form.cleaned_data['comment'],
                              writer_name="html4css1",
                              settings_overrides={'file_insertion_enabled': 0 })
        comment = PageComment(
            page=entry,
            commenter_name=form.cleaned_data['commenter_name'],
            commenter_email=form.cleaned_data['commenter_email'],
            commenter_website=form.cleaned_data['commenter_website'],
            comment=sanitize_html(parts['fragment']),
            state=STATE_PUBLISHED)
        comment.save()
        vobject.request.message = _(u"Your comment has been added.")
    else:
        vobject.request.pagecommentsform = form
        vobject.request.message = _(
                    u"There was an error in your comment; see below.")
    vobject.request.view_name = 'view'
    return vobject.end_view()


def moderate_comments(vobject, parms=None):
    entry = vobject.rentry.descendant
    if vobject.request.method != 'POST' or not isinstance(entry, PageEntry):
        raise Http404
    querydict = vobject.request.POST
    for k in querydict:
        import re
        m = re.match(r'comment_(\d+)_state', k)
        if not m: continue
        comment = PageComment.objects.get(id=int(m.group(1)))
        e = comment.page
        e.request = vobject.request
        if not permissions.EDIT in e.permissions:
            # FIXME: Should add a user message here
            continue
        comment.state = querydict[k]
        comment.save()
    vobject.request.view_name = 'view'
    return vobject.end_view()
