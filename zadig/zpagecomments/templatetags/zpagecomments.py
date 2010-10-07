from django import template
from django.utils.translation import ugettext as _
from django.utils.html import escape

from zadig.zstandard.models import PageEntry
from zadig.zpagecomments.models import PageComment, CommentForm, \
                                                STATE_PUBLISHED,STATE_DELETED

register = template.Library()


class PageCommentsNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        result = ''
        vobject = context.get('vobject', None)
        entry = vobject.rentry.descendant
        if not isinstance(entry, PageEntry): return result
        comments = PageComment.objects.filter(page=entry,
                state__in=(STATE_PUBLISHED, STATE_DELETED)).order_by('id')
        for c in comments:
            authorline = _(u'<span class="author">%s</span> says:') % (
                                            escape(c.commenter_name),)
            if c.state==STATE_DELETED:
                body = '<p class="notice">%s</p>' % (
                    _(u'This comment has been deleted by an administrator.'),)
            else:
                body = '<p class="comment">%s</p>' % (c.comment,)
            result += '''<div class="pageComment">
                <p class="authorLine">%s</p>
                <p class="date">%s</p>
                %s
                </div>''' % (authorline, c.date.isoformat(), body)
        form = CommentForm()
        result += '''<div class="addComment">
           %s
           <p class="heading">%s</p>
           <p class="notice">%s</p>
           <form method="POST" action="%s__zpagecomments.add_comment__/">
           <table>
           %s
           <th></th><td><input type="submit" value="%s" /></td>
           </table>
           </form>
           </div>''' % (form.media, _(u"Add comment"),
                _(u"Your email address will not be published"),
                entry.spath, form.as_table(), _(u"Add comment"))
        return result


def do_pagecomments(parser, token):
    return PageCommentsNode()


register.tag('pagecomments', do_pagecomments)
