from django.db import transaction
from django.core import urlresolvers
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
import django.contrib.auth.models
import settings

class permissions:
    VIEW=1
    EDIT=2
    ADMIN=3
    DELETE=4
    SEARCH=5

class Language(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    def __unicode__(self):
        return self.id
    class Meta:
        db_table = 'cms_language'

class Permission(models.Model):
    descr = models.CharField(max_length=31)
    def __unicode__(self):
        return self.descr
    class Meta:
        db_table = 'cms_permission'

class Lentity(models.Model):
    """A Lentity represents either a user or a group, and is used whenever any
    of the two can be used; for example, a certain permission can be given
    either to a user or to a group.  Either user, or group, or special, must
    be not null; the other two must be null. If user is not null, the Lentity
    represents a user. If group is not null, the Lentity represents a group. If
    special is 1, it represents the anonymous user, and if special is 2, it
    represents all valid users (the logged on user)."""
    user = models.ForeignKey(django.contrib.auth.models.User, null=True)
    group = models.ForeignKey(django.contrib.auth.models.Group, null=True)
    special = models.PositiveSmallIntegerField(null=True)
    def __unicode__(self):
        return "user=%s, group=%s, special=%s" % (str(self.user),
            str(self.group), str(self.special))
    class Meta:
        unique_together = ('user', 'group')
        db_table = "cms_lentity"
    def save(self, force_insert=False, force_update=False):
        """Verify integrity before saving."""
        if (not self.user and not self.group and self.special in (1, 2)) \
        or (self.user and not self.group and not self.special) \
        or (not self.user and self.group and not self.special):
            return super(Lentity, self).save(force_insert, force_update)
        raise Exception("Invalid Lentity: " + self.__unicode__())

class State(models.Model):
    descr = models.CharField(max_length=31)
    def __unicode__(self):
        return self.descr
    class Meta:
        db_table = 'cms_state'

class StatePermission(models.Model):
    state = models.ForeignKey(State)
    lentity = models.ForeignKey(Lentity)
    permission = models.ForeignKey(Permission)
    def __unicode__(self):
        return "state=%s, %s, permission=%s" (self.state, self.lentity,
                                                            self.permission)
    class Meta:
        unique_together = ('lentity', 'permission')
        db_table = 'cms_statepermission'

class StateTransition(models.Model):
    source_state = models.ForeignKey(State, related_name='source_rules')
    target_state = models.ForeignKey(State, related_name='target_rules')
    def __unicode__(self):
        return "%s => %s" % (self.source_state, self.target_state)
    class Meta:
        unique_together = ('source_state', 'target_state')
        db_table = 'cms_statetransition'

class Workflow(models.Model):
    name = models.CharField(max_length=127, unique=True)
    states = models.ManyToManyField(State)
    state_transitions = models.ManyToManyField(StateTransition)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'cms_workflow'

class Site(models.Model):
    name = models.SlugField(max_length=100, unique=True)
    language = models.ForeignKey(Language)
    workflow = models.ForeignKey(Workflow)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'cms_site'

class EntryManager(models.Manager):
    def get_by_path(self, request, site, path):
        entry=None
        for name in path.split('/'):
            entry = self.get(site__name=site, name=name, container=entry)
            if not permissions.VIEW in entry.get_permissions(request):
                return None
        return entry

class Entry(models.Model):
    site = models.ForeignKey(Site)
    container = models.ForeignKey('self', related_name="all_subentries",
                                  blank=True, null=True)
    name = models.SlugField(max_length=100, blank=True)
    seq = models.PositiveIntegerField()
    owner = models.ForeignKey(django.contrib.auth.models.User)
    state = models.ForeignKey(State)
    objects = EntryManager()
    def __init__(self, *args, **kwargs):
        # If called with only three arguments, then it is someone calling the
        # twistyCMS API, and the three arguments are request, site_name, path.
        # Otherwise, it is likely Django calling us in the default Django way.
        if len(args)!=3 or kwargs:
            return super(Entry, self).__init__(*args, **kwargs)
        (request, site_name, path) = args
        names = path.split('/')
        parent_path = '/'.join(names[:-1])
        parent_entry = Entry.objects.get_by_path(request,site_name, parent_path)
        if not permissions.EDIT in parent_entry.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        site = Site.objects.get(name=site_name)
        siblings = Entry.objects.filter(container=parent_entry)
        if siblings.count():
            max_seq = siblings.order_by('-seq')[0].seq
        else:
            max_seq = 0
        initial_state = Workflow.objects.get(id=settings.WORKFLOW_ID) \
            .state_transitions.get(source_state__descr="Nonexistent") \
            .target_state
        return super(Entry, self).__init__(site=site, container=parent_entry,
            name=names[-1], owner=request.user, state=initial_state,
            seq = max_seq+1)
    def get_permissions(self, request):
        if request.user.is_authenticated() and self.owner.pk == request.user.pk:
            return set((permissions.VIEW, permissions.EDIT, permissions.ADMIN,
                permissions.DELETE, permissions.SEARCH))
        result = set()
        if request.user.is_authenticated():
            lentities = [Lentity.objects.get(user=request.user),
                         Lentity.objects.get(special=2)]
            lentities.append(Lentity.objects.filter(
                                          group__in=request.user.groups.all()))
        else:
            lentities = [Lentity.objects.get(special=1)]
        for lentity in lentities:
            for perm in EntryPermission.objects.filter(lentity=lentity,
                                                              entry=self):
                result.add(perm.permission_id)
            for perm in StatePermission.objects.filter(lentity=lentity,
                                                              state=self.state):
                result.add(perm.permission_id)
        return result
    def get_vobject(self, request, version_number=None):
        latest_vobject = self.vobject_set.latest()
        if version_number is None:
            vobject = latest_vobject
        else:
            vobject = self.vobject_set.get(version_number=version_number)
        if vobject.version_number != latest_vobject.version_number \
                and permissions.EDIT not in self.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        return vobject
    @property
    def path(self):
        result = self.name
        entry = self
        while entry.container:
            entry = entry.container
            result = entry.name + '/' + result
        return result
    @property
    def url(self):
        return urlresolvers.reverse('twistycms.core.views.view_object',
            kwargs = { 'site': self.site.name, 'path': self.path })
    def contains(self, entry):
        while entry:
            if entry.container == self: return True
            entry = entry.container
        return False
    def get_subentries(self, request):
        parent_permissions = self.get_permissions(request)
        if permissions.VIEW not in parent_permissions:
            raise PermissionDenied(_(u"Permission denied"))
        subentries = self.all_subentries.order_by('seq').all()
        if permissions.EDIT in parent_permissions:
            return subentries
        result = []
        for s in subentries:
            if permissions.SEARCH in s.get_permissions(request):
                result.append(s)
        return result
    @transaction.commit_manually
    def reorder(self, request, source_seq, target_seq):
        if permissions.EDIT not in self.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        try:
            subentries = self.all_subentries.order_by('seq').all()
            s = source_seq
            t = target_seq
            n = len(subentries)
            if s<1 or s>n or t<1 or t>n+1 or s==t:
                raise Exception(_("Invalid reordering operation"))
            subentries[s-1].seq = 32767
            subentries[s-1].save()
            if t>s:
                for i in range(source_seq+1, t):
                    subentries[i-1].seq = i-1
                    subentries[i-1].save()
                subentries[s-1].seq = t-1
                subentries[s-1].save()
            else:
                for i in range(s-1, t-1, -1):
                    subentries[i-1].seq = i+1
                    subentries[i-1].save()
                subentries[s-1].seq = t
                subentries[s-1].save()
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
    def __unicode__(self):
        result = self.name
        container = self.container
        while container:
            result = container.name + '/' + result
            container = container.container
        return self.site.__unicode__() + result
    class Meta:
        unique_together = (('site', 'container', 'name'),
                           ('site', 'container', 'seq'))
        db_table = 'cms_entry'
        ordering = ('site__id', 'container__id', 'seq')

class EntryPermission(models.Model):
    entry = models.ForeignKey(Entry)
    lentity = models.ForeignKey(Lentity)
    permission = models.ForeignKey(Permission)
    def __unicode__(self):
        return "entry=%s, %s, permission=%s" (self.entry, self.lentity,
                                                            self.permission)
    class Meta:
        unique_together = ('lentity', 'permission')
        db_table = 'cms_entrypermission'

class VObjectManager(models.Manager):
    def get_by_path(self, request, site, path, version_number=None):
        entry = Entry.objects.get_by_path(request, site, path)
        return entry.get_vobject(request, version_number)

class VObject(models.Model):
    entry = models.ForeignKey(Entry, related_name="vobject_set")
    version_number = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, blank=True, null=True)
    objects = VObjectManager()
    def __unicode__(self):
        return '%s v. %d' % (self.entry.__unicode__(), self.version_number)
    class Meta:
        ordering = ('entry', 'version_number')
        unique_together = ('entry', 'version_number')
        get_latest_by = "date"
        db_table = 'cms_vobject'
        permissions = (("view", "View"),)

class MetatagManager(models.Manager):
    def default(self):
        first_metatags = self.all()[0]
        vobject_language = first_metatags.vobject.language
        a = self.filter(language=vobject_language)
        if a: return a[0]
        return first_metatags

class VObjectMetatags(models.Model):
    vobject = models.ForeignKey(VObject, related_name="metatags")
    language = models.ForeignKey(Language)
    title = models.CharField(max_length=250)
    short_title = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    def __unicode(self):
        return '%s %s metatags' % (self.vobject.__unicode__(),
                                   self.language)
    class Meta:
        unique_together = ('vobject', 'language')
        db_table = 'cms_vobjectmetatags'
    objects = MetatagManager()

class ContentFormat(models.Model):
    descr = models.CharField(max_length=20)
    def __unicode__(self):
        return self.descr
    class Meta:
        db_table = 'cms_contentformat'

class Page(VObject):
     format = models.ForeignKey(ContentFormat)
     content = models.TextField(blank=True)
     class Meta:
        db_table = 'cms_page'

class File(VObject):
    content = models.FileField(upload_to="files")
    class Meta:
        db_table = 'cms_file'

class Image(VObject):
    content = models.ImageField(upload_to="images")
    class Meta:
        db_table = 'cms_image'

# I don't know how these two will evolve. If the original idea
# remains, likely NewsItem and Event are also required, subclassing
# Page.
#class NewsItemVersion(PageVersion):
#    pass
#class EventVersion(PageVersion):
#    pass

#class LinkVersion(ObjectVersion):
#    target = models.TextField()

#class InternalRedirection(Object):
#    target = models.ForeignKey(Object)
