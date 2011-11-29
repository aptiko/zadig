from django.http import Http404
from django.utils.translation import ugettext as _

from zadig.core.models import PERM_EDIT
from zadig.core.decorators import require_POST
from zadig.zstandard.models import PageEntry
from zadig.zpagecomments.models import PageComment, CommentForm, \
                                       EntryOptionSet, STATE_PUBLISHED


@require_POST
def add_comment(vobject):
    request = vobject.request
    entry = vobject.entry.descendant
    if not isinstance(entry, PageEntry):
        raise Http404
    try:
        if not entry.ZpagecommentsEntryOptions.allow_comments: raise Http404
    except EntryOptionSet.DoesNotExist:
        raise Http404
    form = CommentForm(request.POST)
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
        request.message = _(u"Your comment has been added.")
    else:
        request.pagecommentsform = form
        request.message = _(
                    u"There was an error in your comment; see below.")
    request.action = 'view'
    return vobject.action_view()


@require_POST
def moderate_comments(vobject):
    request = vobject.request
    entry = vobject.entry.descendant
    if not isinstance(entry, PageEntry):
        raise Http404
    querydict = request.POST
    for k in querydict:
        import re
        m = re.match(r'comment_(\d+)_state', k)
        if not m: continue
        comment = PageComment.objects.get(id=int(m.group(1)))
        e = comment.page
        if not PERM_EDIT in e.permissions:
            # FIXME: Should add a user message here
            continue
        comment.state = querydict[k]
        comment.save()
    request.action = 'view'
    return vobject.action_view()
