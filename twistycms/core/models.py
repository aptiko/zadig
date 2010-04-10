import mimetypes

from django.db import transaction
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import django.contrib.auth.models
from django.core.servers.basehttp import FileWrapper
from django import forms
import settings

from twistycms.core import utils
import twistycms.core

from twistycms.core.utils import primary_buttons
from twistycms.core.utils import secondary_buttons

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

class EntryManager(models.Manager):
    def get_by_path(self, request, path):
        entry=None
        for name in utils.split_path(path):
            entry = self.get(name=name, container=entry)
            if not permissions.VIEW in entry.get_permissions(request):
                return None
        return entry

class Entry(models.Model):
    object_class = models.CharField(max_length=100)
    container = models.ForeignKey('self', related_name="all_subentries",
                                  blank=True, null=True)
    name = models.SlugField(max_length=100, blank=True)
    seq = models.PositiveIntegerField()
    owner = models.ForeignKey(django.contrib.auth.models.User)
    state = models.ForeignKey(State)
    objects = EntryManager()
    def __init__(self, *args, **kwargs):
        # If called with only two arguments, then it is someone calling the
        # twistyCMS API, and the two arguments are request and path.
        # Otherwise, it is likely Django calling us in the default Django way.
        if len(args)!=2 or kwargs:
            result = super(Entry, self).__init__(*args, **kwargs)
        else:
            (request, path) = args
            names = path.split('/')
            parent_path = '/'.join(names[:-1])
            parent_entry = Entry.objects.get_by_path(request, parent_path)
            if not permissions.EDIT in parent_entry.get_permissions(request):
                raise PermissionDenied(_(u"Permission denied"))
            siblings = Entry.objects.filter(container=parent_entry)
            if siblings.count():
                max_seq = siblings.order_by('-seq')[0].seq
            else:
                max_seq = 0
            initial_state = Workflow.objects.get(id=settings.WORKFLOW_ID) \
                .state_transitions.get(source_state__descr="Nonexistent") \
                .target_state
            result = super(Entry, self).__init__(container=parent_entry,
                name=names[-1], owner=request.user, state=initial_state,
                seq = max_seq+1)
        if not self.object_class:
            self.object_class = self._meta.object_name
    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        else:
            return getattr(self, self.object_class.lower())
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
        latest_vobject = self.vobject_set.order_by('-version_number')[0]
        if version_number is None:
            vobject = latest_vobject
        else:
            vobject = self.vobject_set.get(version_number=version_number)
        if vobject.version_number != latest_vobject.version_number \
                and permissions.EDIT not in self.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        for x in ('page', 'image'):
            if hasattr(vobject, x):
                return getattr(vobject, x)
        return vobject
    @property
    def path(self):
        result = self.name
        entry = self
        while entry.container and entry.container.name:
            entry = entry.container
            result = entry.name + '/' + result
        return result
    @property
    def spath(self):
        result = '/' + self.path + '/'
        if result == '//':
            result = '/'
        return result
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
    def add_details(self, vobject, form):
        raise NotImplementedError("This functionality is only available "
            +"in sublcasses")
    def edit_view(self, request, new=False):
        # FIXME: form.name ignored when editing
        assert self.object_class.endswith('Entry'), \
            "Assertion failed:%s" % (self.object_class,)
        entry_type = self.object_class[:-5]
        vobject_class = eval('V' + entry_type)
        editform = eval('Edit%sForm' % (entry_type,))
        applet_options = [o for o in twistycms.core.applet_options
                                                        if o['entry_options']]
        if new:
            vobject = self.container.get_vobject(request).descendant
            path = self.container.path
        else:
            vobject = self.get_vobject(request).descendant
            path = self.path
        if request.method != 'POST':
            if new:
                form = editform(initial={ 'language': vobject.language.id })
            else:
                form = editform(initial={
                    'language': vobject.language.id,
                    'name': vobject.entry.name,
                    'title': vobject.metatags.default().title,
                    'short_title': vobject.metatags.default().short_title,
                    'description': vobject.metatags.default().description,
                    'content': vobject.content
                })
            for o in applet_options:
                o['entry_options_form'] = o['entry_options'](request, path)
        else:
            form = editform(request.POST, request.FILES)
            for o in applet_options:
                o['entry_options_form'] = o['EntryOptionsForm'](request.POST)
            all_forms_are_valid = all((form.is_valid(),) +
                                    tuple([o['entry_options_form'].is_valid()
                                            for o in applet_options]))
            if all_forms_are_valid:
                if new:
                    # FIXME: Code duplication with Entry.__init__
                    if not permissions.EDIT in self.container.get_permissions(request):
                        raise PermissionDenied(_(u"Permission denied"))
                    self.name = form.cleaned_data['name']
                    self.seq = 1
                    siblings = Entry.objects.filter(container=self.container)
                    if siblings.count():
                        self.seq = siblings.order_by('-seq')[0].seq + 1
                    self.owner = request.user
                    self.state = Workflow.objects.get(id=settings.WORKFLOW_ID) \
                        .state_transitions \
                        .get(source_state__descr="Nonexistent").target_state
                    self.save()
                nvobject = vobject_class(entry=self,
                    version_number=new and 1 or (vobject.version_number + 1),
                    language=Language.objects.get(
                                              id=form.cleaned_data['language']))
                self.add_details(nvobject, form)
                nvobject.save()
                nmetatags = VObjectMetatags(
                    vobject=nvobject,
                    language=nvobject.language,
                    title=form.cleaned_data['title'],
                    short_title=form.cleaned_data['short_title'],
                    description=form.cleaned_data['description'])
                nmetatags.save()
                for o in applet_options:
                    o['entry_options'](request, self.path,
                                                        o['entry_options_form'])
                return HttpResponseRedirect(self.spath+'__view__/')
        return render_to_response('edit_%s.html' % (entry_type.lower()),
              { 'request': request, 'vobject': vobject, 'form': form,
                'applet_options': applet_options,
                'primary_buttons': primary_buttons(request, vobject, 'edit'),
                'secondary_buttons': secondary_buttons(request, vobject)})
    def contents_view(self, request):
        subentries = self.get_subentries(request)
        vobject = self.get_vobject(request)
        if request.method == 'POST':
            move_item_form = MoveItemForm(request.POST)
            if move_item_form.is_valid():
                s = move_item_form.cleaned_data['move_object']
                t = move_item_form.cleaned_data['before_object']
                self.reorder(request, s, t)
        else:
            move_item_form = MoveItemForm(initial=
                {'num_of_objects': len(subentries)})
        return render_to_response('entry_contents.html',
                { 'request': request, 'vobject': vobject,
                  'subentries': subentries, 'move_item_form': move_item_form,
                  'primary_buttons': primary_buttons(request, vobject, 'contents'),
                  'secondary_buttons': secondary_buttons(request, vobject)})
    def history_view(self, request):
        vobject = self.get_vobject(request)
        return render_to_response('entry_history.html',
                { 'request': request, 'vobject': vobject,
                  'primary_buttons': primary_buttons(request, vobject, 'history'),
                  'secondary_buttons': secondary_buttons(request, vobject)})
    def __unicode__(self):
        result = self.name
        container = self.container
        while container:
            result = container.name + '/' + result
            container = container.container
        return result
    class Meta:
        unique_together = (('container', 'name'),
                           ('container', 'seq'))
        db_table = 'cms_entry'
        ordering = ('container__id', 'seq')

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
    def get_by_path(self, request, path, version_number=None):
        entry = Entry.objects.get_by_path(request, path)
        return entry.get_vobject(request, version_number)

class VObject(models.Model):
    object_class = models.CharField(max_length=100)
    entry = models.ForeignKey(Entry, related_name="vobject_set")
    version_number = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, blank=True, null=True)
    objects = VObjectManager()
    def save(self, *args, **kwargs):
        if not self.object_class:
            self.object_class = self._meta.object_name
        return super(VObject, self).save(args, kwargs)
    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        else:
            return getattr(self, self.object_class.lower())
    def end_view(self, request):
        raise NotImplementedError("Method should be redefined in derived class")
    def info_view(self, request):
        raise NotImplementedError("Method should be redefined in derived class")
    def __unicode__(self):
        return '%s v. %d' % (self.entry.__unicode__(), self.version_number)
    class Meta:
        ordering = ('entry', 'version_number')
        unique_together = ('entry', 'version_number')
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
    def get_short_title(self):
        return self.short_title or self.title
    class Meta:
        unique_together = ('vobject', 'language')
        db_table = 'cms_vobjectmetatags'
    objects = MetatagManager()

class EditForm(forms.Form):
    # FIXME: metatags should be in many languages
    language = forms.ChoiceField(choices=[(l, l) for l in settings.LANGUAGES])
    name = forms.CharField(required=False,
        max_length=Entry._meta.get_field('name').max_length)
    title = forms.CharField(
        max_length=VObjectMetatags._meta.get_field('title').max_length)
    short_title = forms.CharField(required=False, max_length=
        VObjectMetatags._meta.get_field('short_title').max_length)
    description = forms.CharField(widget=forms.Textarea, required=False)

class MoveItemForm(forms.Form):
    move_object = forms.IntegerField()
    before_object = forms.IntegerField()
    num_of_objects = forms.IntegerField(widget=forms.HiddenInput)
    def clean(self):
        s = self.cleaned_data['move_object']
        t = self.cleaned_data['before_object']
        n = self.cleaned_data['num_of_objects']
        if s<1 or s>n:
            raise forms.ValidationError(
                                _("The specified object to move is incorrect"))
        if t<1 or t>n+1:
            raise forms.ValidationError(
                   _("The specified target position is incorrect; "
                    +"use up to one more than the existing number of objects"))
        if s==t or t==s+1:
            raise forms.ValidationError(
             _("You can't move an object before itself or before the next one; "
              +"this would leave it in the same position"))
        return self.cleaned_data

### Page ###

class ContentFormat(models.Model):
    descr = models.CharField(max_length=20)
    def __unicode__(self):
        return self.descr
    class Meta:
        db_table = 'cms_contentformat'

class PageEntry(Entry):
    def add_details(self, vobject, form):
        vobject.format=ContentFormat.objects.get(descr='html')
        vobject.content=utils.sanitize_html(form.cleaned_data['content'])
    class Meta:
        db_table = 'cms_pageentry'

class VPage(VObject):
    format = models.ForeignKey(ContentFormat)
    content = models.TextField(blank=True)
    def end_view(self, request):
        return render_to_response('view_page.html', { 'request': request,
            'vobject': self,
            'primary_buttons': primary_buttons(request, self, 'view'),
            'secondary_buttons': secondary_buttons(request, self)})
    def info_view(self, request):
        return self.end_view(request)
    class Meta:
        db_table = 'cms_vpage'

class EditPageForm(EditForm):
    from tinymce.widgets import TinyMCE
    content = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30},
        mce_attrs={
            'content_css': '/static/style.css',
            'convert_urls': False,
            'theme': 'advanced',
            'theme_advanced_blockformats': 'p,h1,h2',
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_toolbar_align': 'left',
            'theme_advanced_buttons1': 'bold,italic,justifyleft,justifycenter,justifyright,numlist,bullist,outdent,indent,removeformat,image,link,unlink,anchor,code,formatselect',
            'theme_advanced_buttons2': '',
            'theme_advanced_buttons3': '',
        }), required=False)

#class File(VObject):
#    entry = models.ForeignKey(PageEntry, related_name="vobject_set")
#    content = models.FileField(upload_to="files")
#    class Meta:
#        db_table = 'cms_file'

### Image ###

class ImageEntry(Entry):
    def add_details(self, vobject, form):
        vobject.content=form.cleaned_data['content']
    class Meta:
        db_table = 'cms_imageentry'

class VImage(VObject):
    content = models.ImageField(upload_to="images")
    def end_view(self, request):
        content_type = mimetypes.guess_type(self.content.path)[0]
        wrapper = FileWrapper(open(self.content.path))
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-length'] = self.content.size
        return response
    def info_view(self, request):
        return render_to_response('view_image.html', { 'request': request,
            'vobject': self,
            'primary_buttons': primary_buttons(request, self, 'view'),
            'secondary_buttons': secondary_buttons(request, self)})
    class Meta:
        db_table = 'cms_vimage'

class EditImageForm(EditForm):
    content = forms.ImageField()

#class LinkVersion(VObject):
#    target = models.TextField()

### InternalRedirection ###

class InternalRedirectionEntry(Entry):
    class Meta:
        db_table = 'cms_internalredirectionentry'

class VInternalRedirection(VObject):
    target = models.ForeignKey(Entry)
    def end_view(self, request):
        return HttpResponsePermanentRedirect(self.target.spath)
    def info_view(self, request):
        return render_to_response('view_internalredirection.html',
            { 'request': request, 'vobject': self,
              'primary_buttons': primary_buttons(request, self, 'view'),
              'secondary_buttons': secondary_buttons(request, self)} )
    class Meta:
        db_table = 'cms_vinternalredirection'

class EditInternalRedirectionForm(EditForm):
    pass
