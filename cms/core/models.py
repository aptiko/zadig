from django.db import models
import django.contrib.auth.models

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
    def get_query_set(self):
        return super(EntryManager, self).get_query_set() # More to follow in order to check permissions

class Entry(models.Model):
    site = models.ForeignKey(Site)
    container = models.ForeignKey('self', related_name="subentries",
                                  blank=True, null=True)
    name = models.SlugField(max_length=100, blank=True)
    seq = models.PositiveIntegerField()
    owner = models.ForeignKey(django.contrib.auth.models.User)
    state = models.ForeignKey(State)
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

class VObject(models.Model):
    entry = models.ForeignKey(Entry, related_name="vobject_set")
    version_number = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, blank=True, null=True)
    def __unicode__(self):
        return '%s v. %d' % (self.entry.__unicode__(), self.version_number)
    class Meta:
        ordering = ('entry', 'version_number')
        unique_together = ('entry', 'version_number')
        get_latest_by = "date"
        db_table = 'cms_vobject'
        permissions = (("view", "View"),)

class MetatagManager(models.Manager):
    "Adds the 'default' method that returns the default set of metatags."
    def default(self):
        return self.get(language=self.all()[0].vobject.language)

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
