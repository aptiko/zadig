from django import template
from django.utils.translation import ugettext as _

from zadig.zstandard.models import PageEntry
from zadig.zpagecomments.models import PageComment, CommentForm, EntryOptionSet

register = template.Library()


class PageCommentsNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        result = ''
        vobject = context.get('vobject', None)
        entry = vobject.rentry.descendant
        if not isinstance(entry, PageEntry): return result
        optionset, created = EntryOptionSet.objects.get_or_create(entry=entry)
        if created: optionset.save()
        if not optionset.allow_comments: return result
        if vobject.request.view_name not in ('view', 'info'): return result
        comments = PageComment.objects.filter(page=entry).order_by('id')
        for c in comments:
            result += c.render(vobject.request)

        if 'pagecommentsform' in vobject.request.__dict__:
            form = vobject.request.pagecommentsform
        else:
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
