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
            container = vobject.rentry.rcontainer
            vobject = container.vobject if container else None
        return result

def do_breadcrumbs(parser, token):
    return BreadcrumbsNode()

register.tag('breadcrumbs', do_breadcrumbs)

### Language tools ###

class LanguageToolsNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        vobject = context.get('vobject', None)
        if not vobject: return ''
        entry = vobject.rentry
        alt_lang_entries = entry.alt_lang_entries if entry else []
        result = u'<div onMouseOver="showShowables(this)" '+\
                                        'onMouseOut="hideShowables(this)">'
        result += u'<ul>' 
        preferred_lang_id = vobject.request.preferred_language
        effective_lang_id = vobject.request.effective_language
        preferred_lang_name = coremodels.Language.objects.get(
                                                    id=preferred_lang_id).descr
        effective_lang_name = coremodels.Language.objects.get(
                                                    id=effective_lang_id).descr
        object_available_in_preferred_lang = False
        for lang in settings.LANGUAGES:
            target = vobject.request.path
            for e in alt_lang_entries:
                if e.vobject.language.id==lang:
                    target = e.spath
                    if lang==preferred_lang_id:
                        object_available_in_preferred_lang = True
            result += u'<li class="%s %s %s"><a href="%s?set_language=%s">%s' \
                      '</a></li>' % (
                      'effective' if effective_lang_id==lang else "",
                      'preferred' if preferred_lang_id==lang else "",
                      'available' if target!=vobject.request.path else "",
                      target, lang, 
                      coremodels.Language.objects.get(id=lang).descr)
        result += u'</ul><p class="showable">'
        result += _(u'Your preferred language is set to %s (click on another '
                    'language to change it).') % (preferred_lang_name,)
        if preferred_lang_id!=effective_lang_id:
            result += _(u' However, the object you are viewing is in %s') % (
                        effective_lang_name,)
            if object_available_in_preferred_lang:
                result += _(u'; click "%s" to view it in %s.') % (
                    preferred_lang_name, preferred_lang_name)
            else:
                result += _(u', and it is not available in %s.') % (
                    preferred_lang_name,)
        result += u'</p>'
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
        request = context['vobject'].request
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
    def render_entry_contents(self, entry, current_entry, level):
        result = ''
        siblings = [x for x in entry.subentries
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
                        v.language.id!=entry.request.effective_language and \
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
                s.vobject.metatags.default().get_short_title())
            if s.contains(current_entry) or s.id==current_entry.id:
                result += self.render_entry_contents(s, current_entry, level+1)
            result += '</li>'
        if result: result += '</ul>'
        return result
    def render(self, context):
        vobject = context.get('vobject', None)
        # Find the innermost containing object that has navigation_toplevel.
        toplevel_entry = vobject.rentry
        try:
            while True:
                if toplevel_entry.path=='': break
                entryoptions = models.EntryOptions.objects.get(
                                                        entry=toplevel_entry)
                if entryoptions.navigation_toplevel: break
                toplevel_entry = toplevel_entry.rcontainer
        except models.EntryOptions.DoesNotExist:
            pass
        result = self.render_entry_contents(toplevel_entry, vobject.rentry, 1)
        if result:
            result = '''<dl class="portlet navigationPortlet">
                <dt><a href='%s'>%s</a></dt>
                <dd class="lastItem">%s</dd></dl>''' % (toplevel_entry.spath,
                toplevel_entry.vobject.metatags.default().get_short_title(),
                result)
        return result
            
def do_navigation(parser, token):
    return NavigationNode()

register.tag('navigation', do_navigation)
