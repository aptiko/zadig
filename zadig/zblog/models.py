from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django import forms
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from zadig.core.models import Entry, VObject, entry_types, PERM_VIEW
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

    class SubscribeForm(forms.Form):
        email = forms.EmailField()
        comments = forms.BooleanField(required=False)

    def subscribe_view(self, parms=None):
        subscriber, form = None, None
        if parms:
            if parms.endswith('/'): parms = parms[:-1]
            subscriber = BlogEmailSubscriber.activate(parms)
        else:
            form = self.SubscribeForm(self.request.POST) \
                    if self.request.method=='POST' else self.SubscribeForm()
            if self.request.method=='POST' and form.is_valid():
                subscriber = BlogEmailSubscriber.subscribe(
                                            form.cleaned_data['email'],
                                            self, form.cleaned_data['comments'])
                subscriber.email_activation_key(
                                    self.vobject.metatags.default.title, self)
        return render_to_response('blog_subscribe.html', {
            'vobject': self.vobject, 'form': form, 'subscriber': subscriber },
            context_instance=RequestContext(self.request))
        

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

    def state_view(self, parms):
        anonuser = AnonymousUser()
        was_published = PERM_VIEW in self.user_permissions(anonuser)
        result = super(BlogPostEntry, self).state_view(parms)
        is_published = PERM_VIEW in self.user_permissions(anonuser)
        if is_published and not was_published:
            BlogEmailSubscriber.notify_subscribers(self)
        return result

entry_types.append(BlogPostEntry)


### Other models ###


class EmailSubscriber(models.Model):
    email = models.EmailField()
    date_subscribed = models.DateTimeField()
    activation_key = models.CharField(max_length=40, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def activate(cls, key):
        subscriber = get_object_or_404(cls, activation_key=key)
        subscriber.activation_key = ''
        subscriber.save()
        return subscriber

    def create_activation_key(self):
        from django.utils.hashcompat import sha_constructor
        import random
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.activation_key = sha_constructor(salt+self.email).hexdigest()
        return self.activation_key

    def email_activation_key(self, description, entry):
        email_subject = _(u'Blog subscription confirmation')
        email_body = _(u'To confirm that you want to subscribe to %s, '
            'follow the link below:\n%s__subscribe__/%s/') % (description,
                    entry.absolute_uri, self.activation_key)
        send_mail(email_subject, email_body, 'noreply@nowhere.no', [self.email])
                     
class BlogEmailSubscriber(EmailSubscriber):
    blog = models.ForeignKey(BlogEntry)
    comments = models.BooleanField(default=False)

    @classmethod
    def subscribe(cls, email, blog, comments=False):
        from datetime import datetime
        subscriber = cls(email=email, blog=blog, comments=comments,
            date_subscribed=datetime.now())
        subscriber.create_activation_key()
        subscriber.save()
        return subscriber

    @classmethod
    def notify_subscribers(cls, blogpost):
        blog_mt = blogpost.container.vobject.metatags.default
        post_mt = blogpost.vobject.metatags.default
        e_subject = "%s: %s" % (blog_mt.get_short_title(), post_mt.title)
        e_body = _(u"A new article has been published in %s,\n"
                u"of which you are a subscriber; you can read it at\n%s") % (
                blog_mt.title, blogpost.permalink)
        for s in cls.objects.filter(activation_key=""):
            send_mail(e_subject, e_body, 'noreply@nowhere.no', [s.email])


class BlogPostEmailSubscriber(EmailSubscriber):
    blogpost = models.ForeignKey(BlogPostEntry)

    @classmethod
    def subscribe(cls, email, blogpost, comments=False):
        from datetime import datetime
        subscriber = cls(email=email, blog=blogpost,
                                        date_subscribed=datetime.now())
        subscriber.create_activation_key()
        subscriber.save()
        return subscriber
