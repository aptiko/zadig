import mimetypes

from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.db import models
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import django.contrib.auth.models
from django import forms
import settings

from twistycms.core import utils
import twistycms.core

from twistycms.core.utils import primary_buttons, secondary_buttons

class permissions:
    VIEW=1
    EDIT=2
    ADMIN=3
    DELETE=4
    SEARCH=5

class Language(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    descr = models.CharField(max_length=63)
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


class MultilingualGroup(models.Model):

    def check(self):
        entries = list(self.entry_set)
        if len(entries)==1:
            raise ValidationError(_(u"The MultilingualGroup (id=%d) contains "
                "only one Entry (id=%d)") % (self.id, entries[0].id))
        if not len(entries):
            raise ValidationError(_(u"The MultilingualGroup (id=%d) does not "
                "contain any Entry") % (self.id,))
        languages_in_group = set()
        for entry in entries:
            latest_vobject = entry.vobject_set.order_by('-version_number')[0]
            if not latest_vobject.language:
                raise ValidationError(_(u"The MultilingualGroup (id=%d) "
                    "contains Entry (id=%d) which does not have a language") %
                    (self.id, entry.id))
            if latest_vobject.language.id in languages_in_group:
                raise ValidationError(_(u"The MultilingualGroup (id=%d) "
                    "contains multiple occurrences of language %s (the "
                    "entries are %s)") % (self.id, latest_vobject.language.id,
                    ', '.join([str(x) for x in entries])))
            languages_in_group.add(latest_vobject.language.id)

    def __unicode__(self):
        return unicode(self.id)

    class Meta:
        db_table = 'cms_multilingualgroup'


class _check_multilingual_group(object):
    """Called whenever one needs to verify the integrity of specified
    multilingual group. What it actually does is postpone this check for
    commit time."""
    # FIXME: This implementation is not thread-safe.
    groups_to_check = set()
    def __init__(self, mgid):
        self.groups_to_check.add(mgid)


def _check_pending_multilingual_groups(sender, **kwargs):
    for mgid in _check_multilingual_group.groups_to_check:
        MultilingualGroup.objects.get(id=mgid).check()
from django.core.signals import request_finished
request_finished.connect(_check_pending_multilingual_groups)


class EntryManager(models.Manager):
    def get_by_path(self, request, path):
        entry=None
        for name in utils.split_path(path):
            try:
                entry = self.get(name=name, container=entry)
            except Entry.DoesNotExist:
                return None
            if not permissions.VIEW in entry.get_permissions(request):
                return None
        entry.request = request
        return entry


class Entry(models.Model):
    object_class = models.CharField(max_length=100)
    container = models.ForeignKey('self', related_name="all_subentries",
                                  blank=True, null=True)
    name = models.SlugField(max_length=100, blank=True)
    seq = models.PositiveIntegerField()
    owner = models.ForeignKey(django.contrib.auth.models.User)
    state = models.ForeignKey(State)
    multilingual_group = models.ForeignKey(MultilingualGroup, blank=True,
                                                                null=True)
    objects = EntryManager()

    def __init__(self, *args, **kwargs):
        # If called with only two arguments, then it is someone calling the
        # twistyCMS API, and the two arguments are request and path.
        # Otherwise, it is likely Django calling us in the default Django way.
        if len(args)!=2 or kwargs:
            result = super(Entry, self).__init__(*args, **kwargs)
            self.request = None
        else:
            (request, path) = args
            names = path.split('/')
            parent_path = '/'.join(names[:-1])
            parent_entry = Entry.objects.get_by_path(request, parent_path)
            super(Entry, self).__init__()
            self.container = parent_entry
            self.name = names[-1]
            self.request = request
            self.__initialize(request)
        if not self.object_class:
            self.object_class = self._meta.object_name

    def __initialize(self, request):
        """Set all other attributes of a newly created Entry, when only
        container has been set."""
        if not permissions.EDIT in self.container.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        self.seq = 1
        siblings = Entry.objects.filter(container=self.container)
        if siblings.count():
            self.seq = siblings.order_by('-seq')[0].seq + 1
        self.owner = request.user
        self.state = Workflow.objects.get(id=settings.WORKFLOW_ID) \
            .state_transitions \
            .get(source_state__descr="Nonexistent").target_state

    def save(self, *args, **kwargs):
        if self.multilingual_group:
            _check_multilingual_group(self.multilingual_group.id)
        # If this is an update, also check the multilingual group to which 
        # this entry originally belonged. FIXME: This solution is a bit ugly;
        # check http://stackoverflow.com/questions/2029814/keeping-track-of-changes-since-the-last-save-in-django-models
        if self.id:
            original_mg = Entry.objects.get(id=self.id).multilingual_group
            if original_mg:
                _check_multilingual_group(original_mg.id)
        return super(Entry, self).save(args, kwargs)

    def delete(self, *args, **kwargs):
        if self.multilingual_group:
            _check_multilingual_group(self.multilingual_group.id)
        return super(Entry, self).delete(args, kwargs)

    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        else:
            return getattr(self, self.object_class.lower())

    @property
    def permissions(self):
        return self.get_permissions(self.request)

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

    @property
    def vobject(self):
        return self.get_vobject(self.request)

    def get_vobject(self, request, version_number=None):
        latest_vobject = self.vobject_set.order_by('-version_number')[0]
        if version_number is None:
            vobject = latest_vobject
        else:
            vobject = self.vobject_set.get(version_number=version_number)
        if vobject.version_number != latest_vobject.version_number \
                and permissions.EDIT not in self.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
        a = vobject.descendant
        a.request = request
        return a

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

    @property
    def subentries(self):
        return self.get_subentries(self.request)

    def get_subentries(self, request):
        parent_permissions = self.get_permissions(request)
        if permissions.VIEW not in parent_permissions:
            raise PermissionDenied(_(u"Permission denied"))
        subentries = self.all_subentries.order_by('seq').all()
        if permissions.EDIT in parent_permissions:
            return list(subentries)
        result = []
        for s in subentries:
            if permissions.SEARCH in s.get_permissions(request):
                result.append(s)
        return result

    def reorder(self, request, source_seq, target_seq):
        if permissions.EDIT not in self.get_permissions(request):
            raise PermissionDenied(_(u"Permission denied"))
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

    @property
    def template_name(self):
        return 'edit_entry.html'

    def __create_metatags_formset(self, request, new):
        """Return a formset of metatags forms, as many as existing metatag sets
        plus one if there is another available language. Called by edit_view()
        method. """
        initial = []
        if new:
            vobject = self.container.get_vobject(request).descendant
            initial.append({ 'language': vobject.language.id })
        else:
            vobject = self.get_vobject(request).descendant
            used_langs = []
            for m in vobject.metatags.all():
                initial.append({'language': m.language.id, 'title': m.title,
                    'short_title': m.short_title, 'description': m.description})
                used_langs.append(m.language.id)
            remaining_langs = set(settings.LANGUAGES).difference(used_langs)
            if remaining_langs:
                initial.append({ 'language': remaining_langs.pop() })
        return MetatagsFormSet(initial=initial)

    def __process_metatags_formset(self, vobject, metatagsformset):
        for m in metatagsformset.cleaned_data:
            if not (m['title'] or m['short_title'] or m['description']):
                continue
            nmetatags = VObjectMetatags(vobject=vobject,
                language=Language.objects.get(id=m['language']),
                title=m['title'], short_title=m['short_title'],
                description=m['description'])
            nmetatags.save()

    def edit_view(self, request, new=False):
        applet_options = [o for o in twistycms.core.applet_options
                                                        if o['entry_options']]
        if request.method != 'POST':
            mainform = EditEntryForm(initial={ 'name': self.name,
                        'language': self.vobject.language, })
            metatagsformset = self.__create_metatags_formset(request, new)
            subform = self.create_edit_subform(request, new)
            optionsforms = [o['entry_options'](request, self.path)
                                                        for o in applet_options]
        else:
            mainform = EditEntryForm(request.POST)
            metatagsformset = MetatagsFormSet(request.POST)
            subform = self.subform_class(request.POST, request.FILES)
            optionsforms = [o['EntryOptionsForm'](request.POST)
                                                        for o in applet_options]
            all_forms_are_valid = all(
                [mainform.is_valid(),
                 metatagsformset.is_valid(),
                 subform.is_valid() ] +
                [o.is_valid() for o in optionsforms])
            if all_forms_are_valid:
                if new:
                    self.__initialize(request)
                    self.name = mainform.cleaned_data['name']
                    self.save()
                nvobject = self.vobject_class(entry=self,
                    version_number=new and 1 or (
                                self.get_vobject(request).version_number + 1),
                    language=Language.objects.get(
                                       id=mainform.cleaned_data['language']))
                self.process_edit_subform(nvobject, subform)
                nvobject.save()
                self.__process_metatags_formset(nvobject, metatagsformset)
                for o,f in map(lambda x,y:(x,y), applet_options, optionsforms):
                    o['entry_options'](request, self.path, f)
                if mainform.cleaned_data['name'] != self.name:
                    self.rename(request, mainform.cleaned_data['name'])
                return HttpResponseRedirect(self.spath+'__view__/')
        if new:
            vobject = self.container.get_vobject(request)
        else:
            vobject = self.get_vobject(request)
        return render_to_response(self.template_name,
              { 'request': request, 'vobject': vobject,
                'mainform': mainform, 'metatagsformset': metatagsformset,
                'subform': subform, 'optionsforms': optionsforms,
                'primary_buttons': 
                        primary_buttons(request, not new and vobject, 'edit'),
                'secondary_buttons':
                    not new and secondary_buttons(request, vobject) or []})

    def rename(self, request, newname):
        if not self.container:
            raise ValueError(_("The root page cannot be renamed"))
        for sibling in self.container.all_subentries.all():
            if sibling.id == self.id: continue
            if sibling.name == newname:
                raise ValueError(_("Cannot rename; target name already exists"))
        oldname = self.name
        self.name = newname
        self.save()
        nentry = InternalRedirectionEntry(container=self.container)
        nentry.__initialize(request)
        nentry.name = oldname
        nentry.save()
        nvobject = VInternalRedirection(entry=nentry,
            version_number=1,
            language=self.get_vobject(request).language,
            target=self)
        nvobject.save()
        nmetatags = VObjectMetatags(
            vobject=nvobject,
            language=nvobject.language,
            title=_("Redirection"))
        nmetatags.save()

    def move(self, request, target_entry):
        if not self.container:
            raise ValueError(_("The root page cannot be moved"))
        if self.container.id == target_entry.id:
            return
        for nsibling in target_entry.all_subentries.all():
            if nsibling.name == self.name:
                raise ValueError(_("Cannot move; an entry with the same name at the target location already exists"))
        if (permissions.EDIT not in target_entry.get_permissions(request)) \
                or (permissions.DELETE not in self.get_permissions(request)):
            raise PermissionDenied(_("Permission denied"))
        oldcontainer = self.container
        oldseq = self.seq
        self.seq = target_entry.all_subentries.count() + 1
        self.container = target_entry
        self.save()
        nentry = InternalRedirectionEntry(container=oldcontainer)
        nentry.__initialize(request)
        nentry.seq = oldseq
        nentry.name = self.name
        nentry.save()
        nvobject = VInternalRedirection(entry=nentry,
            version_number=1,
            language=self.get_vobject(request).language,
            target=self)
        nvobject.save()
        nmetatags = VObjectMetatags(
            vobject=nvobject,
            language=nvobject.language,
            title=_("Redirection"))
        nmetatags.save()

    def contents_view(self, request):
        subentries = self.subentries
        vobject = self.vobject
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
        if self.entry.multilingual_group:
            _check_multilingual_group(self.entry.multilingual_group.id)
        return super(VObject, self).save(args, kwargs)

    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        else:
            return getattr(self, self.object_class.lower())

    @property
    def rentry(self):
        entry = self.entry
        entry.request = self.request
        return entry

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

class EditEntryForm(forms.Form):
    language = forms.ChoiceField(choices=[(l, l) for l in settings.LANGUAGES])
    name = forms.CharField(required=False,
                        max_length=Entry._meta.get_field('name').max_length)

class MetatagsForm(forms.Form):
    language = forms.ChoiceField(choices=[(l, l) for l in settings.LANGUAGES])
    title = forms.CharField(required=False,
                max_length=VObjectMetatags._meta.get_field('title').max_length)
    short_title = forms.CharField(required=False, max_length=
                VObjectMetatags._meta.get_field('short_title').max_length)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'cols':'40', 'rows': '5'}), required=False)
    def clean(self):
        c = self.cleaned_data
        if not c['title'] and (c['short_title'] or c['description']):
            raise forms.ValidationError(_(u"When you specify a short "
                    +"title or description, you must also specify a title"))
        return c

from django.forms.formsets import BaseFormSet, formset_factory
class BaseMetatagsFormSet(BaseFormSet):
    def clean(self):
        used_langs = []
        for f in self.forms:
            if not f.is_valid():
                # There are errors already, don't check further
                return super(BaseMetatagsFormSet, self).clean()
            c = f.cleaned_data
            if not c['title']:
                continue
            if c['language'] in used_langs:
                raise forms.ValidationError(_(u"Language %s used more than "
                        +"once") % (c['language'],))
            used_langs.append(c['language'])
        if not used_langs:
            raise forms.ValidationError(_(u"You must specify a title"))
        return super(BaseMetatagsFormSet, self).clean()

    fieldlabels = {'language':    _(u'Language'),
                   'title':       _(u'Title'),
                   'short_title': _(u'Short title'),
                   'description': _(u'Description')}
    def as_wide_table(self):
        from django.utils.safestring import mark_safe
        from django.forms.forms import BoundField
        result = '''<tr><td colspan="3">%s
                    <input type="hidden" name="form-TOTAL_FORMS" value="%s" />
                    <input type="hidden" name="form-INITIAL_FORMS" value="%s" />
                    </td></tr>''' % (self.non_form_errors(), len(self.forms),
                    len(self.forms))
        for i in range(0, len(self.forms), 2):
            result += u'<tr><td></td><td>%s</td><td>%s</td></tr>' % (
                self.forms[i].non_field_errors(),
                i+1<len(self.forms) and self.forms[i+1].non_field_errors() or '')
            lfields = [(n, f) for n, f in self.forms[i].fields.items()]
            rfields = [('',''), ('',''), ('',''), ('','')]
            if i+1<len(self.forms):
                rfields = [(n, f) for n, f in self.forms[i+1].fields.items()]
            all_fields = map(lambda x,y:(x[0],x[1],y[0],y[1]), lfields, rfields)
            for lname, lfield, rname, rfield in all_fields:
                lbf = BoundField(self.forms[i], lfield, lname)
                rbf = ''
                if i+1<len(self.forms):
                    rbf = BoundField(self.forms[i+1], rfield, rname)
                result += u'<tr><th>%s:</th><td>%s</td><td>%s</td>' % (
                    self.fieldlabels[lname], lbf, rbf)
        return mark_safe(result)
MetatagsFormSet = formset_factory(MetatagsForm, formset=BaseMetatagsFormSet,
                                                                        extra=0)

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
    def create_edit_subform(self, request, new):
        if new:
            result = EditPageForm()
        else:
            result = EditPageForm(
                    initial={'content': self.get_vobject(request).content})
        return result
    def process_edit_subform(self, vobject, form):
        vobject.format=ContentFormat.objects.get(descr='html')
        vobject.content=utils.sanitize_html(form.cleaned_data['content'])
    @property
    def template_name(self):
        return 'edit_page.html'
    @property
    def subform_class(self):
        return EditPageForm
    @property
    def vobject_class(self):
        return VPage
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

class EditPageForm(forms.Form):
    from tinymce.widgets import TinyMCE
    content = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30},
        mce_attrs={
            'content_css': '/static/style.css',
            'convert_urls': False,
            'theme': 'advanced',
            'theme_advanced_blockformats': 'p,h1,h2',
            'theme_advanced_styles': 'Float Left=floatLeft,Float Right=floatRight,Align Top=alignTop',
            'theme_advanced_toolbar_location': 'top',
            'theme_advanced_toolbar_align': 'left',
            'theme_advanced_buttons1': 'bold,italic,justifyleft,justifycenter,justifyright,numlist,bullist,outdent,indent,removeformat,image,link,unlink,anchor,code,formatselect,styleselect',
            'theme_advanced_buttons2': '',
            'theme_advanced_buttons3': '',
            'popup_css': '/static/tinymce_popup.css',
        }), required=False)
    def render(self):
        return self['content']

### Image ###

class ImageEntry(Entry):
    def create_edit_subform(self, request, new):
        if new:
            result = EditImageForm()
        else:
            result = EditImageForm(
                    initial={'content': self.get_vobject(request).content})
        return result
    def process_edit_subform(self, vobject, form):
        vobject.content=form.cleaned_data['content']
    @property
    def subform_class(self):
        return EditImageForm
    @property
    def vobject_class(self):
        return VImage
    class Meta:
        db_table = 'cms_imageentry'

class VImage(VObject):
    content = models.ImageField(upload_to="images")
    def end_view(self, request):
        from django.core.servers.basehttp import FileWrapper
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

class EditImageForm(forms.Form):
    content = forms.ImageField()
    def render(self):
        return self.as_table()

### Link ###

class LinkEntry(Entry):
    def process_edit_subform(self, vobject, form):
        vobject.target = form.cleaned_data['target']
    def create_edit_subform(self, request, new):
        if new:
            result = EditLinkForm()
        else:
            result = EditLinkForm(
                    initial={'target': self.get_vobject(request).target})
        return result
    @property
    def subform_class(self):
        return EditLinkForm
    @property
    def vobject_class(self):
        return VLink
    class Meta:
        db_table = 'cms_linkentry'

class VLink(VObject):
    target = models.URLField()
    def end_view(self, request):
        # FIXME: This should not work like this, it should directly link outside
        from django.http import HttpResponsePermanentRedirect
        return HttpResponsePermanentRedirect(self.target)
    def info_view(self, request):
        return render_to_response('view_link.html',
            { 'request': request, 'vobject': self,
              'primary_buttons': primary_buttons(request, self, 'view'),
              'secondary_buttons': secondary_buttons(request, self)} )
    class Meta:
        db_table = 'cms_vlink'

class EditLinkForm(forms.Form):
    target = forms.URLField()
    def render(self):
        return self.as_table()

### InternalRedirection ###

# FIXME: Should subclass link or something

class InternalRedirectionEntry(Entry):
    def process_edit_subform(self, vobject, form):
        vobject.target = form.cleaned_data['target']
    def create_edit_subform(self, request, new):
        if new:
            result = EditInternalRedirectionForm()
        else:
            result = EditInternalRedirectionForm(
                    initial={'target': self.get_vobject(request).target})
        return result
    @property
    def subform_class(self):
        return EditInternalRedirectionForm
    @property
    def vobject_class(self):
        return VInternalRedirection
    class Meta:
        db_table = 'cms_internalredirectionentry'

class VInternalRedirection(VObject):
    target = models.ForeignKey(Entry)
    def end_view(self, request):
        from django.http import HttpResponsePermanentRedirect
        return HttpResponsePermanentRedirect(self.target.spath)
    def info_view(self, request):
        return render_to_response('view_internalredirection.html',
            { 'request': request, 'vobject': self,
              'primary_buttons': primary_buttons(request, self, 'view'),
              'secondary_buttons': secondary_buttons(request, self)} )
    class Meta:
        db_table = 'cms_vinternalredirection'

class EditInternalRedirectionForm(forms.Form):
    target = forms.ChoiceField()
    def __init__(self, **kwargs):
        EditInternalRedirectionForm.base_fields['target'].choices = [
                                (e.id, e.spath) for e in Entry.objects.all()]
        super(EditInternalRedirectionForm, self).__init__(**kwargs)
    def render(self):
        return self.as_table()
