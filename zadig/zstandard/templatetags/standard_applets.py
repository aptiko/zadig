# coding: UTF-8
from django import template
from django.utils.translation import ugettext as _
from django.conf import settings

from zadig.core.models import Entry, Language, entry_types
from zadig.core.utils import get_current_path
from zadig.zstandard import models

register = template.Library()


### Breadcrumbs ###


class BreadcrumbsNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        result = ''
        vobject = context.get('vobject', None)
        while vobject:
            entryoptions = models.EntryOptionSet.objects.get_or_create(
                                                        entry=vobject.entry)[0]
            if not entryoptions or not entryoptions.no_breadcrumbs:
                if result:
                    result = u'''<a href="%s">%s</a>
                        <span class="breadcrumb-separator">→</span> %s''' % (
                        vobject.entry.spath,
                        vobject.metatags.default.get_short_title(), result)
                else:
                    result = vobject.metatags.default.get_short_title()
            container = vobject.entry.container
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
        request = context.get('request', None)
        if not vobject: return ''
        entry = vobject.entry
        alt_lang_entries = entry.alt_lang_entries if entry else []
        result = u'<div onMouseOver="showShowables(this)" '+\
                                        'onMouseOut="hideShowables(this)">'
        result += u'<ul>' 
        preferred_lang_id = request.preferred_language
        effective_lang_id = request.effective_language
        preferred_lang_name = Language.objects.get(id=preferred_lang_id).descr
        effective_lang_name = Language.objects.get(id=effective_lang_id).descr
        object_available_in_preferred_lang = False
        for (lang, langdescr) in settings.ZADIG_LANGUAGES:
            target = request.path
            for e in alt_lang_entries:
                if e.vobject.language.id==lang:
                    target = e.spath
                    if lang==preferred_lang_id:
                        object_available_in_preferred_lang = True
            result += u'<li class="%s %s %s"><a href="%s?set_language=%s">%s' \
                      '</a></li>' % (
                      'effective' if effective_lang_id==lang else "",
                      'preferred' if preferred_lang_id==lang else "",
                      'available' if target!=request.path else "",
                      target, lang, Language.objects.get(id=lang).descr)
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
        self.multilingual_groups_seen = set()

    def __must_show(self, sibling, parent_entry, current_entry):
        if sibling.contains(current_entry) or sibling.id==current_entry.id:
            return True
        v = sibling.vobject
        if not v.language: return True
        if v.language.id==self.request.effective_language: return True
        if not v.entry.multilingual_group: return True
        if self.request.effective_language in [e.vobject.language.id
                                        for e in v.entry.alt_lang_entries]:
            return False
        if v.entry.multilingual_group.id in self.multilingual_groups_seen:
            return False
        return True

    def render_entry_contents(self, entry, current_entry, level):
        result = ''
        siblings = [x for x in entry.subentries
               if x.object_class in ('PageEntry','LinkEntry', 'NewsItemEntry')]
        no_sibling_shown_yet = True
        for s in siblings:
            v = s.vobject
            try:
                entryoptions = models.EntryOptionSet.objects.get(entry=s)
                if entryoptions.no_navigation: continue
            except models.EntryOptionSet.DoesNotExist:
                pass
            if not self.__must_show(s, entry, current_entry):
                continue
            if no_sibling_shown_yet:
                no_sibling_shown_yet = False
                result += '<ul class="navigationLevel%d">' % (level,)
            result += '<li><a class="state%s %s" href="%s">%s</a>' % (
                s.state.descr.replace(' ',''),
                s.id=='current' if current_entry.id else '',
                s.spath,
                s.vobject.metatags.default.get_short_title())
            if s.multilingual_group:
                self.multilingual_groups_seen.add(s.multilingual_group.id)
            if s.contains(current_entry) or s.id==current_entry.id:
                result += self.render_entry_contents(s, current_entry, level+1)
            result += '</li>'
        if result: result += '</ul>'
        return result

    def render(self, context):
        if 'vobject' not in context: return ''
        vobject = context['vobject']
        self.request = context['request']
        # Find the innermost containing object that has navigation_toplevel.
        toplevel_entry = vobject.entry
        while True:
            if not toplevel_entry.container: break
            entryoptions = models.EntryOptionSet.objects.get_or_create(
                                                    entry=toplevel_entry)[0]
            if entryoptions.navigation_toplevel: break
            toplevel_entry = toplevel_entry.container
        result = self.render_entry_contents(toplevel_entry, vobject.entry, 1)
        if result:
            toplevel_link = toplevel_entry.spath
            preferred_language = self.request.preferred_language
            if (toplevel_entry.vobject.language and
                    toplevel_entry.vobject.language.id != preferred_language):
                for e in toplevel_entry.alt_lang_entries:
                    if e.vobject.language.id == preferred_language:
                        toplevel_link = e.spath
                        break
            result = '''<dl class="portlet navigationPortlet">
                <dt><a href='%s'>%s</a></dt>
                <dd>%s</dd></dl>''' % (toplevel_link,
                toplevel_entry.vobject.metatags.default.get_short_title(),
                result)
        return result
            

def do_navigation(parser, token):
    return NavigationNode()


register.tag('navigation', do_navigation)


### News ###


class NewsNode(template.Node):

    def render(self, context):
        vobject = context.get('vobject', None)
        if vobject is None: return ''
        request = context['request']
        news_items = models.NewsItemEntry.objects.exclude_language_duplicates(
                request.effective_language).order_by(
                                    '-vobject__vpage__vnewsitem__news_date')
        if not news_items.count():
            return ''
        result = '<dl class="portlet NewsPortlet"><dt>%s</dt>' % (_(u"News"),)
        item_type = 'odd'
        for i, e in enumerate(news_items):
            result = result + '<dd class="%s">' \
                        '<a class="state%s" href="%s">%s</a>' \
                        '<span class="details">%s</span></dd>' % (item_type,
                        e.state.descr.replace(' ', ''),
                        e.spath, e.vobject.metatags.default.get_short_title(),
                        e.vobject.descendant.news_date.isoformat()[:10])
            item_type = 'even' if item_type=='odd' else 'odd'
            if i==4: break
        result += '</dl>'
        return result


def do_news(parser, token):
    return NewsNode()


register.tag('news', do_news)


### Events ###


class EventsNode(template.Node):

    def render(self, context):
        from datetime import datetime
        vobject = context.get('vobject', None)
        if vobject is None: return ''
        request = context['request']
        events = models.EventEntry.objects.exclude_language_duplicates(
            request.effective_language).filter(
            vobject_set__vpage__vevent__event_start__gt=datetime.now()
            ).order_by('vobject_set__vpage__vevent__event_start')
        if not events.count():
            return ''
        result = '<dl class="portlet EventsPortlet"><dt>%s</dt>' % (
                                                                _(u"Events"),)
        item_type = 'odd'
        for i, e in enumerate(events):
            result = result + '<dd class="%s">' \
                        '<a class="state%s" href="%s">%s</a>' \
                        '<span class="details">%s</span></dd>' % (item_type,
                        e.state.descr.replace(' ', ''),
                        e.spath, e.vobject.metatags.default.get_short_title(),
                        e.vobject.descendant.event_start.isoformat()[:10])
            item_type = 'even' if item_type=='odd' else 'odd'
            if i==4: break
        result += '</dl>'
        return result


def do_events(parser, token):
    return EventsNode()


register.tag('events', do_events)


### Primary buttons ###


class PrimaryButtonsNode(template.Node):

    actions = ( ('contents', _(u'contents')), ('info', _(u'view')),
              ('edit', _(u'edit')), ('history', _(u'history')),
              ('permissions', _(u'permissions')) )

    def __init__(self):
        pass

    def render(self, context):
        if 'vobject' not in context: return ''
        vobject = context['vobject']
        request = context['request']
        if not vobject:
            return '<ul class="primaryButtons">' \
               '<li class="selected"><a href="">%s</a></li></ul>' % _(u'new')
        if not vobject.entry.touchable: return ''
        result = '<ul class="primaryButtons">'
        for actionname, actionstring in self.actions:
            href = '__' + actionname + '__/'
            current_action = request.action
            if current_action=='view': current_action='info'
            result += '<li %s><a href="%s">%s</a></li>' % ('class="selected"'
                      if actionname==current_action else '', href, actionstring)
        result += '</ul>'
        return result


def do_primary_buttons(parser, token):
    return PrimaryButtonsNode()


register.tag('primary_buttons', do_primary_buttons)


### Secondary buttons ###


class SecondaryButtonsNode(template.Node):

    def __init__(self):
        pass

    def render(self, context):
        if 'vobject' not in context: return ''
        vobject = context['vobject']
        request = context['request']
        if not vobject: return ''
        spath = vobject.entry.spath
        if not vobject.entry.touchable: return ''
        p =[{ 'name': _(u'State: <span class="state%s">%s</span>') %
                    (vobject.entry.state.descr, vobject.entry.state.descr),
              'items': [ { 'name': x.descr,
                           'post': {'action': 'change_state', 'state': x.id },
                         } for x in vobject.entry.possible_target_states
                        ]
            },
            { 'name': _(u'Add new…'),
              'items': [{ 'href': '%s__new__/%s/' % (spath, cls.__name__[:-5]),
                          'name': cls.typename } for cls in entry_types
                          if cls.can_be_contained(vobject.entry.descendant)]
            },
            { 'name': _(u'Actions'),
              'items': [ { 'name': _(u'Cut'),
                           'post': { 'action': 'cut' }},
                         { 'name': _(u'Paste'),
                           'post': { 'action': 'paste' }},
                         { 'name': _(u'Delete'),
                           'post': { 'action': 'delete' }}
                         ]
            },
            ]
        result = u'<ul class="secondaryButtons">'
        for b in p:
            result += u'<li><dl><dt><a href="" onclick=' \
                u'"return toggleMenu(this.parentNode)">%s&#9660;' \
                '</a></dt><dd>' % b['name']
            for i in b['items']:
                if i.has_key('post'):
                    result += u'<li><form method="POST" action="%s">' \
                        '<input type="hidden" name="csrfmiddlewaretoken" ' \
                                                                'value="%s">' \
                        '<input type="submit" value="%s">' % (
                        spath, request.COOKIES.get('csrftoken'), 
                        i['name'])
                    for k in i['post'].keys():
                        result += '<input type="hidden" name="%s" value="%s">' \
                                % (k, i['post'][k])
                    result += '</form></li>'
                else:
                    result += u'<li><a href="%s">%s</a></li>' % (i['href'],
                                                                 i['name'])
            result += u'</dd></dl></li>'
        result += u'</ul>'
        return result


def do_secondary_buttons(parser, token):
    return SecondaryButtonsNode()


register.tag('secondary_buttons', do_secondary_buttons)
