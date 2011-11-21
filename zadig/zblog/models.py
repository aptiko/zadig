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
    def action_view(self):
        return render_to_response('view_blog.html', { 'vobject': self },
                context_instance = RequestContext(self.request))

    def action_info(self):
        return self.action_view()


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
        #comments = forms.BooleanField(required=False)

    def action_subscribe(self):
        subscriber, form = None, None
        parms = request.parms
        if parms:
            if parms.endswith('/'): parms = parms[:-1]
            subscriber = BlogEmailSubscriber.confirm(parms)
        else:
            form = self.SubscribeForm(self.request.POST) \
                    if self.request.method=='POST' else self.SubscribeForm()
            if self.request.method=='POST' and form.is_valid():
                subscriber = BlogEmailSubscriber.subscribe_or_unsubscribe(
                                            form.cleaned_data['email'],
                                            self, False) #form.cleaned_data['comments'])
                subscriber.email_confirmation_key(
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

    def action_change_state(self):
        anonuser = AnonymousUser()
        was_published = PERM_VIEW in self.user_permissions(anonuser)
        result = super(BlogPostEntry, self).action_change_state(request.parms)
        is_published = PERM_VIEW in self.user_permissions(anonuser)
        if is_published and not was_published:
            BlogEmailSubscriber.notify_subscribers(self)
        return result

entry_types.append(BlogPostEntry)


### Other models ###


class EmailSubscriber(models.Model):
    email = models.EmailField(unique=True)
    date_requested = models.DateTimeField()
    subscribed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=40, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def confirm(cls, key):
        from datetime import datetime, timedelta
        cls.objects.filter(date_requested__lt=datetime.now()-timedelta(1)
                                                                    ).delete()
        subscriber = get_object_or_404(cls, confirmation_key=key)
        subscriber.confirmation_key = ''
        if subscriber.subscribed:
            subscriber.subscribed = False
            subscriber.delete()
        else:
            subscriber.subscribed = True
            subscriber.save()
        return subscriber

    def create_confirmation_key(self):
        from django.utils.hashcompat import sha_constructor
        import random
        if not self.confirmation_key:
            salt = sha_constructor(str(random.random())).hexdigest()[:5]
            self.confirmation_key = sha_constructor(salt+self.email).hexdigest()
        return self.confirmation_key

    def email_confirmation_key(self, description, entry):
        email_subject = _(u'Blog subscription confirmation')
        if self.subscribed:
            message = _(u'You are already subscribed to %s.\n\n'
                u'Clicking on the link below will UNSUBSCRIBE you:\n')
        else:
            message = _(u'To confirm that you want to subscribe to %s, '
            u'follow the link below:\n')
        email_body = (message + '%s__subscribe__/%s/') % (description,
                    entry.absolute_uri, self.confirmation_key)
        send_mail(email_subject, email_body, settings.ZBLOG_FROM_EMAIL,
                                                                [self.email])
                     
class BlogEmailSubscriber(EmailSubscriber):
    blog = models.ForeignKey(BlogEntry)
    comments = models.BooleanField(default=False)

    @classmethod
    def subscribe_or_unsubscribe(cls, email, blog, comments=False):
        from datetime import datetime
        subscriber = cls.objects.get_or_create( email=email, blog=blog,
            defaults={ 'comments': comments, 'date_requested': datetime.now()})[0]
        subscriber.create_confirmation_key()
        subscriber.save()
        return subscriber

    @classmethod
    def notify_subscribers(cls, blogpost):
        blog_mt = blogpost.container.vobject.metatags.default
        post_mt = blogpost.vobject.metatags.default
        e_subject = "[%s] %s" % (blog_mt.get_short_title(), post_mt.title)
        e_body = _(u"A new article has been published in %s,\n"
                u"of which you are a subscriber; you can read it at\n%s") % (
                blog_mt.title, blogpost.permalink)
        for s in cls.objects.filter(confirmation_key=""):
            send_mail(e_subject, e_body, settings.ZBLOG_FROM_EMAIL, [s.email])


class BlogPostEmailSubscriber(EmailSubscriber):
    blogpost = models.ForeignKey(BlogPostEntry)
