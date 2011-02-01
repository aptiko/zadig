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
        request = context['request']
        entry = vobject.entry.descendant
        if not isinstance(entry, PageEntry): return result
        optionset, created = EntryOptionSet.objects.get_or_create(entry=entry)
        if created: optionset.save()
        if not optionset.allow_comments: return result
        if request.view_name not in ('view', 'info'): return result
        comments = PageComment.objects.filter(page=entry).order_by('id')
        for c in comments:
            result += c.render(request)
        if result.find('</select>')>=0:
            result = '''<form method="POST"
                            action="__zpagecomments.moderate_comments__/">
                        <input type="submit" value="%s" />
                        %s
                        <input type="submit" value="%s" />
                        </form>''' % (_(u"Submit all state changes"), result,
                                    _(u"Submit all state changes"))
        if 'pagecommentsform' in request.__dict__:
            form = request.pagecommentsform
        else:
            form = CommentForm()
        result += '''<div class="addComment">
           %s
           <p class="heading">%s</p>
           <p class="notice">%s</p>
           <form method="POST" action="%s__zpagecomments.add_comment__/">
           <table>
           %s
           <tr><th></th><td><p class="notice">%s</p></td></tr>
           <tr><th></th><td><input type="submit" value="%s" /></td></tr>
           </table>
           </form>
           </div>''' % (form.media, _(u"Add comment"),
                _(u"Your email address will not be published"),
                entry.spath, form.as_table(),
                _(u'Separate paragraphs with blank line; URLs will be '
                  u'automatically converted to links; use **bold**, '
                  u'*italics*; indent paragraphs for block quoting; other '
                  u'<a href="http://docutils.sourceforge.net/docs/user/rst/'
                  u'quickstart.html">reStructuredText</a> markup is also '
                  u'possible.'),
                _(u"Add comment"))
        return result


def do_pagecomments(parser, token):
    return PageCommentsNode()


register.tag('pagecomments', do_pagecomments)
