# -*- encoding: utf-8 -*-

import re

from django.utils.translation import ugettext as _

def split_path(path):
    if path=='' or path=='/': return ['',]
    if path.startswith('/'): path = path[1:]
    if path.endswith('/'): path = path[:-1]
    return ['',] + path.split('/')

def get_current_path(request):
    path = request.path
    assert(path[0] == '/')
    path = path[1:]
    if path.endswith('/'): path = path[:-1]
    path_items = path.split('/')
    for i,p in enumerate(path_items):
        if p.startswith('__') and p.endswith('__'):
            path_items = path_items[:i]
            break
    result = '/' + '/'.join(path_items)
    if result != '/': result += '/'
    return result

def primary_buttons(request, vobject, selected_view):
    from twistycms.core.models import permissions
    if vobject.entry.get_permissions(request).intersection(
            set((permissions.EDIT, permissions.ADMIN))) == set():
        return []
    href_prefix = ''
    if re.search(r'__[a-zA-Z]+__/$', request.path): href_prefix = '../'
    result = []
    for x in (_(u'contents'), _(u'view'), _(u'edit'), _(u'history')):
        href_suffix = '__' + x + '__/'
        if x == _(u'view'): href_suffix = ''
        href = href_prefix + href_suffix
        result.append({ 'name': x, 'href': href, 'selected': x==selected_view })
    return result

def secondary_buttons(request, vobject):
    from twistycms.core.models import permissions
    if vobject.entry.get_permissions(request).intersection(
            set((permissions.EDIT, permissions.ADMIN))) == set():
        return []
    result = [
          { 'name': _(u'State:') + ' ' + vobject.entry.state.descr,
            'items': [
                       { 'href': '__state__/%d' % (x.target_state.id,),
                         'name': x.target_state.descr }
                            for x in vobject.entry.state.source_rules.all()
                     ]
          },
          { 'name': _(u'Add new…'),
            'items': [
                       { 'href': '__newpage__', 'name': _(u'Page') },
                       { 'href': '__newimage__', 'name': _(u'Image') },
                     ]
          },
        ]
    return result
