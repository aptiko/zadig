from django.utils.translation import ugettext as _

from zadig.core.models import user_entry_types
from zadig.zstandard.models import PageEntry, VPage


### Blog ###

class BlogEntry(PageEntry):
    typename = _(u"Blog")

class VBlog(VPage): pass

user_entry_types.append(BlogEntry)


### Blog post ###

class BlogPostEntry(PageEntry):
    typename = _(u"Blog post")

class VBlogPost(VPage): pass

user_entry_types.append(BlogPostEntry)
