# coding: UTF-8
from django import template
from django.utils.translation import ugettext as _
import settings

from twistycms.core import models as coremodels
from twistycms.core.utils import get_current_path
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
                    vobject.entry.spath,
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

### Language tools ###

class LanguageToolsNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        request = context['request']
        vobject = context.get('vobject', None)
        entry = vobject.entry if vobject else None
        alt_lang_entries = entry.alt_lang_entries if entry else []
        result = '<div onMouseOver="showShowables(this)" '+\
                                        'onMouseOut="hideShowables(this)">'
        result += '<ul>' 
        for lang in settings.LANGUAGES:
            target = request.path
            for e in alt_lang_entries:
                if e.vobject.language.id==lang:
                    target = e.spath
            result += '<li %s><a href="%s?set_language=%s">%s</a></li>' % (
                'class="active"' if request.effective_language==lang else "",
                target, lang, coremodels.Language.objects.get(id=lang).descr)
        result += '</ul>'
        result += _('<p class="showable">The preferred language is %s; the '+
                    'effective language is %s.</p>') % (coremodels.Language.
                    objects.get(id=request.preferred_language).descr,
                    coremodels.Language.objects.get(
                                id=request.effective_language).descr)
        result += '</div>'
        return result

def do_language_tools(parser, token):
    return LanguageToolsNode()

register.tag('language_tools', do_language_tools)

### Login ###

class LoginNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        request = context['request']
        if not request.user.is_authenticated():
            return _(u'<a href="%s__login__/">Login</a>' %
                get_current_path(request),)
        return _(u'Welcome %s. <a href="%s__logout__/">Logout</a>' %
            (request.user, get_current_path(request)))

def do_login(parser, token):
    return LoginNode()

register.tag('login', do_login)


### Navigation ###

class NavigationNode(template.Node):
    def __init__(self):
        pass
    def render_entry_contents(self, request, entry, current_entry, level):
        result = ''
        siblings = [x for x in entry.get_subentries(request)
                                if x.object_class in ('PageEntry','LinkEntry')]
        no_sibling_shown_yet = True
        for s in siblings:
            v = s.vobject
            try:
                entryoptions = models.EntryOptions.objects.get(entry=s)
                if entryoptions.no_navigation: continue
            except models.EntryOptions.DoesNotExist:
                pass
            if v.language and \
                        v.language.id!=request.effective_language and \
                        s.id!=current_entry.id and \
                        not s.contains(current_entry):
                continue
            if no_sibling_shown_yet:
                no_sibling_shown_yet = False
                result += '<ul class="navigationLevel%d">' % (level,)
            result += '<li><a class="state%s %s" href="%s">%s</a>' % (
                s.state.descr.replace(' ',''),
                s.id==current_entry.id and 'current' or '',
                s.spath,
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
        # Find the innermost containing object that has navigation_toplevel.
        toplevel_entry = vobject.entry
        try:
            while True:
                if toplevel_entry.path=='': break
                entryoptions = models.EntryOptions.objects.get(
                                                        entry=toplevel_entry)
                if entryoptions.navigation_toplevel: break
                toplevel_entry = toplevel_entry.container
        except models.EntryOptions.DoesNotExist:
            pass
        result = self.render_entry_contents(request, toplevel_entry,
            vobject.entry, 1)
        if result:
            result = '''<dl class="portlet navigationPortlet">
                <dt><a href='%s'>%s</a></dt>
                <dd class="lastItem">%s</dd></dl>''' % (toplevel_entry.spath,
                toplevel_entry.get_vobject(request).metatags.default().get_short_title(),
                result)
        return result
            
def do_navigation(parser, token):
    return NavigationNode()

register.tag('navigation', do_navigation)
