# coding: UTF-8
from django import template
from django.utils.translation import ugettext as _

from twistycms.core import models as coremodels
from twistycms.core import utils
from twistycms.applets.standard import models

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
                    vobject.entry.url,
                    vobject.metatags.default().get_short_title(), result)
            else:
                result = vobject.metatags.default().get_short_title()
            container = vobject.entry.container
            if container:
                vobject = container.get_vobject(context['request'])
            else:
                vobject = None
        return result

def do_breadcrumbs(parser, token):
    return BreadcrumbsNode()

register.tag('breadcrumbs', do_breadcrumbs)

### Login ###

class LoginNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        request = context['request']
        if not request.user.is_authenticated():
            return _(u'<a href="%s__login__/">Login</a>' %
                utils.get_current_path(request),)
        return _(u'Welcome %s. <a href="%s__logout__/">Logout</a>' %
            (request.user, utils.get_current_path(request)))

def do_login(parser, token):
    return LoginNode()

register.tag('login', do_login)


### Navigation ###

class NavigationNode(template.Node):
    def __init__(self):
        pass
    def render_entry_contents(self, request, entry, current_entry, level):
        result = ''
        siblings = entry.get_subentries(request)
        no_sibling_shown_yet = True
        for s in siblings:
            try:
                entryoptions = models.EntryOptions.objects.get(entry=s)
                if entryoptions.no_navigation: continue
            except models.EntryOptions.DoesNotExist:
                pass
            if no_sibling_shown_yet:
                no_sibling_shown_yet = False
                result += '<ul class="navigationLevel%d">' % (level,)
            result += '<li><a class="state%s %s" href="%s">%s</a>' % (
                s.state.descr.replace(' ',''),
                s.id==current_entry.id and 'current' or '',
                s.url,
                s.get_vobject(request).metatags.default().get_short_title())
            if s.contains(current_entry) or s.id==current_entry.id:
                result += self.render_entry_contents(request, s, current_entry,
                                                                    level+1)
            result += '</li>'
        if result: result += '</ul>'
        return result
    def render(self, context):
        vobject = context.get('vobject', None)
        request = context['request']
        result = self.render_entry_contents(request,
            coremodels.Entry.objects.get_by_path(request, ''),
            vobject.entry, 1)
        if result:
            result = '''<dl class="portlet navigationPortlet"><dt>%s</dt>
                     <dd class="lastItem">%s</dd></dl>''' % (_(u"Navigation"),
                     result)
        return result
            
def do_navigation(parser, token):
    return NavigationNode()

register.tag('navigation', do_navigation)
