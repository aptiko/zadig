from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext

from zadig.core.models import Entry, VObject, entry_types
from zadig.zstandard.models import PageEntry, VPage


### Blog ###


class VBlog(VObject):
    def end_view(self, parms=None):
        return render_to_response('view_blog.html', { 'vobject': self },
                context_instance = RequestContext(self.request))

    def info_view(self, parms=None):
        return self.end_view()


class BlogEntry(Entry):
    vobject_class = VBlog
    typename = _(u"Blog")

    @classmethod
    def can_create(cls, parent):
        # Quick hack: only if the user is an admin, and not inside another blog
        return super(BlogEntry, cls).can_create(parent) and \
            parent.request.user.is_superuser and \
            not isinstance(parent, BlogEntry)

    @property
    def posts(self):
        result = [x.descendant for x in self.subentries]
        for x in result:
            if x.object_class != u'BlogPostEntry':
                result.remove(x)
        result.reverse()
        return result
        

entry_types.append(BlogEntry)


### Blog post ###


class VBlogPost(VPage):

    @property
    def top(self):
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(self.content)
        i = 0
        result = str(soup.contents[i])
        length = len(result)
        while True:
            i += 1
            try: n = str(soup.contents[i])
            except IndexError: break
            length += len(n)
            if length>1200: break
            result += n
        return result


class BlogPostEntry(PageEntry):
    vobject_class = VBlogPost
    typename = _(u"Blog post")

    def can_contain(self, cls):
        from zadig.zstandard.models import ImageEntry, FileEntry
        return super(BlogPostEntry, self).can_contain(cls) and (
            issubclass(cls, ImageEntry) or issubclass(cls, FileEntry))
        
    @classmethod
    def can_create(cls, parent):
        return super(BlogPostEntry, cls).can_create(parent) \
                                        and isinstance(parent, BlogEntry)


entry_types.append(BlogPostEntry)
