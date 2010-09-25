# -*- encoding: utf-8 -*-

import re

from django.utils.translation import ugettext as _
import settings

def split_path(path):
    if path=='' or path=='/': return ['',]
    if path.startswith('/'): path = path[1:]
    if path.endswith('/'): path = path[:-1]
    return ['',] + path.split('/')

def join_path(*path_items):
    if len(path_items)==1:
        path_items = path_items[0]
    result = ''
    for p in path_items:
        while p.startswith('/'): p = p[1:]
        while p.endswith('/'): p = p[:-1]
        if p:
            if result: result += '/'
            result += p
    return result

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

class sanitize_html(unicode):
    # FIXME: Still vulnerable to some attacks. Go to
    # http://ha.ckers.org/xss.html. The attacks to which we are vulnerable are:
    #  * & Javascript includes (only Netscape 4.x)
    #  * IMG Embedded commands (part I and II)
    # FIXME: Needs unit testing
    valid_tags = '''p i strong em b u a h1 h2 pre br img table thead tbody th
                    td tr ul ol li blockquote'''.split()
    valid_attrs = 'href src width height class align'.split()
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
            # Remove empty <a> tags
            if tag.name=='a' and not tag.attrs: tag.extract()
        result = soup.renderContents().decode('utf8')
        # I don't understand what the unicode() does below, but if it's not
        # there, then the postgresql_psycopg2 backend causes a ProgrammingError
        # with message "can't adapt" when an attempt is made to save a page.
        return unicode(super(sanitize_html, cls).__new__(cls, result))
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
