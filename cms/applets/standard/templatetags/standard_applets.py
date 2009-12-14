# coding: UTF-8
from django import template
from django.utils.translation import ugettext as _

from cms.core import stdlib
import cms.core.models

register = template.Library()

### Breadcrumbs ###

class BreadcrumbsNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        result = ''
        vobject = context.get('vobject', None)
        while vobject:
            if result:
                result = u'''<a href="%s">%s</a>
                    <span class="breadcrumb-separator">→</span> %s''' % (
                    stdlib.get_entry_url(vobject.entry),
                    vobject.metatags.default().short_title, result)
            else:
                result = vobject.metatags.default().short_title
            container = vobject.entry.container
            if container:
                vobject = container.vobject_set.latest()
            else:
                vobject = None
        return result

def do_breadcrumbs(parser, token):
    return BreadcrumbsNode()

register.tag('breadcrumbs', do_breadcrumbs)

### Navigation ###

class NavigationNode(template.Node):
    def __init__(self):
        pass
    def render_entry_contents(self, request, entry, current_entry, level):
        result = ''
        siblings = stdlib.get_entry_subentries(request, entry)
        for s in siblings:
            if s==siblings[0]:
                result += '<ul class="navigationLevel%d">' % (level,)
            result += '<li><a class="state%s %s" href="%s">%s</a>' % (
                s.state.descr.replace(' ',''),
                s.id==current_entry.id and 'current' or '',
                stdlib.get_entry_url(s),
                stdlib.get_entry_vobject(request, s).metatags.default().short_title)
            if stdlib.contains(s, current_entry) or s.id==current_entry.id:
                result += self.render_entry_contents(request, s, current_entry, level+1)
            result += '</li>'
        if result: result += '</ul>'
        return result
    def render(self, context):
        vobject = context.get('vobject', None)
        request = context['request']
        result = self.render_entry_contents(request,
            stdlib.get_entry_by_path(request, vobject.entry.site.name, ''),
            vobject.entry, 1)
        if result:
            result = '''<dl class="portlet navigationPortlet"><dt>%s</dt>
                     <dd class="lastItem">%s</dd></dl>''' % (_(u"Navigation"),
                     result)
        return result
            
def do_navigation(parser, token):
    return NavigationNode()

register.tag('navigation', do_navigation)
