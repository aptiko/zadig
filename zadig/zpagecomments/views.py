from datetime import datetime

from django.http import Http404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import settings

from zadig.core.decorators import require_POST
from zadig.zstandard.models import PageEntry
from zadig.core.models import PERM_EDIT
from zadig.zpagecomments.models import PageComment, CommentForm, \
            EntryOptionSet, STATE_PUBLISHED, STATE_UNAPPROVED, STATE_DELETED


@require_POST
def change_comment_state(vobject):
    request = vobject.request
    entry = vobject.entry.descendant
    if PERM_EDIT not in entry.permissions:
        raise Http404
    comment = PageComment.objects.get(id=int(request.POST['comment_id']))
    comment.state = request.POST['new_state']
    comment.save()
    return HttpResponseRedirect(entry.spath)


def edit_comment(vobject, parms=None):
    request = vobject.request
    entry = vobject.entry.descendant
    if not isinstance(entry, PageEntry):
        raise Http404
    try:
        if not entry.ZpagecommentsEntryOptions.allow_comments: raise Http404
    except EntryOptionSet.DoesNotExist:
        raise Http404
    comment_id_str = parms.strip('/') if request.method != 'POST' \
                                            else request.POST['comment_id']
    if not comment_id_str:
        # New comment being POSTed
        if request.method != 'POST' or entry.creation_date + \
                        settings.ZPAGECOMMENTS_CLOSE_AFTER > datetime.now():
            raise Http404
        comment = None
    else:
        # Starting to edit existing comment (GET), or posting changes (POST)
        comment = PageComment.objects.get(id=int(comment_id_str))
        if PERM_EDIT not in entry.permissions \
                                    or comment.page.id != entry.pageentry.id:
            raise Http404

    # Case where we start to edit existing comment
    if request.method != 'POST':
        form = CommentForm({ 'comment_id': comment.id,
                'commenter_name': comment.commenter_name,
                'commenter_email': comment.commenter_email,
                'commenter_website': comment.commenter_website,
                'comment': comment.comment_source,
                'comment_state': comment.state })
        return render_to_response('edit_comment.html', RequestContext(request,
                { 'form': form, 'vobject': vobject, 'comment': comment, }))

    # We have a POST
    form = CommentForm(request.POST)
    if not form.is_valid():
        request.pagecommentsform = form
        request.message = _(
                    u"There was an error in your submission; see below.")
        request.action = 'view'
        return vobject.action_view()

    state = form.cleaned_data['comment_state']
    if state not in (STATE_PUBLISHED, STATE_UNAPPROVED, STATE_DELETED):
        raise Http404

    # Create the HTML
    from docutils.core import publish_parts
    from zadig.core.utils import sanitize_html
    parts = publish_parts(source=form.cleaned_data['comment'],
                          writer_name="html4css1",
                          settings_overrides={'file_insertion_enabled': 0 })
    comment_html = sanitize_html(parts['fragment'])

    if comment_id_str:
        # Existing comment
        comment = PageComment.objects.get(id=int(request.POST['comment_id']))
        comment.commenter_name = form.cleaned_data['commenter_name']
        comment.commenter_email = form.cleaned_data['commenter_email']
        comment.commenter_website = form.cleaned_data['commenter_website']
        comment.comment_source = form.cleaned_data['comment']
        comment.comment_html = comment_html
        comment.state = form.cleaned_data['comment_state']
    else:
        # New comment
        comment = PageComment(
            page=entry,
            commenter_name=form.cleaned_data['commenter_name'],
            commenter_email=form.cleaned_data['commenter_email'],
            commenter_website=form.cleaned_data['commenter_website'],
            comment_source=form.cleaned_data['comment'],
            comment_html=comment_html,
            state=STATE_PUBLISHED)
    comment.save()
    return HttpResponseRedirect(entry.spath)
