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
          { 'name': _(u'State: <span class="state%s">%s</span>') %
                (vobject.entry.state.descr, vobject.entry.state.descr),
            'items': [
                       { 'href': '__state__/%d' % (x.target_state.id,),
                         'name': x.target_state.descr,
                       } for x in vobject.entry.state.source_rules.all()
                     ]
          },
          { 'name': _(u'Add new…'),
            'items': [
                       { 'href': '__new__/Page/', 'name': _(u'Page') },
                       { 'href': '__new__/Image/', 'name': _(u'Image') },
                     ]
          },
          { 'name': _(u'Actions'),
            'items': [
                       { 'href': '__cut__/', 'name': _(u'Cut') },
                       { 'href': '__paste__/', 'name': _(u'Paste') },
                     ]
          },
        ]
    return result

class sanitize_html(unicode):
    # FIXME: Still vulnerable to some attacks. Go to
    # http://ha.ckers.org/xss.html. The attacks to which we are vulnerable are:
    #  * & Javascript includes (only Netscape 4.x)
    #  * IMG Embedded commands (part I and II)
    # FIXME: Needs unit testing
    valid_tags = '''p i string b u a h1 h2 pre br img table thead tbody td
                    tr'''.split()
    valid_attrs = 'href src width height class'.split()
    url_attrs = 'href src'.split()
    valid_schemes = 'http https ftp mailto'.split()
    def __new__(cls, html):
        from BeautifulSoup import BeautifulSoup, Comment
        soup = BeautifulSoup(html)
        for c in soup.findAll(text=lambda text: isinstance(text, Comment)):
            c.extract() # Remove comments
        for tag in soup.findAll(True):
            if tag.name not in cls.valid_tags:
                tag.extract()
                continue
            attrs = tag.attrs
            tag.attrs = []
            for attr, val in attrs:
                if attr not in cls.valid_attrs: continue
                if (attr in cls.url_attrs) and not cls.url_is_safe(val):
                    continue
                tag.attrs.append((attr, val))
        result = soup.renderContents().decode('utf8')
        return super(sanitize_html, cls).__new__(cls, result)
    @classmethod
    def url_is_safe(cls, url):
        """Return True if the url is relative or its scheme is in valid_schemes.
        Note that we don't use the Python urlparse library, because apparently
        it follows the RFC, and we also need to account for stupid web browsers
        that don't follow the RFC and will honour deceptive urls like ' j
        avascript:' or similar (http://ha.ckers.org/xss.html for examples).
        What we do is the following: First we unquote the url. Then, if the url
        does not contain a colon, it's relative and it's OK; if a slash
        precedes the first colon, it's relative and it's OK; otherwise, the
        part preceding the colon is considered to be a scheme and it must be
        one of those whitelisted."""
        from urllib import unquote
        (scheme, sep, rest) = unquote(url).partition(':')
        return (not sep) or (scheme.find('/')>=0) or (scheme in
                                                      cls.valid_schemes)
