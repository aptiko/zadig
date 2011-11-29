from django import template
from django.utils.translation import ugettext as _
from django.template.loader import get_template

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
        if vobject is None: return result
        entry = vobject.entry.descendant
        if not isinstance(entry, PageEntry): return result
        optionset, created = EntryOptionSet.objects.get_or_create(entry=entry)
        if created: optionset.save()
        if not optionset.allow_comments: return result
        if request.action not in ('view', 'info'): return result
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
        context['form'] = form
        result += get_template('add_comment.html').render(context)
        return result


def do_pagecomments(parser, token):
    return PageCommentsNode()


register.tag('pagecomments', do_pagecomments)
