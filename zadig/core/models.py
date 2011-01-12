from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User, Group
from django import forms
from django.template import RequestContext
import settings

from zadig.core import utils
from zadig.core import entry_types, entry_option_sets


PERM_VIEW=1
PERM_EDIT=2
PERM_ADMIN=3
PERM_DELETE=4
PERM_SEARCH=5

EVERYONE=100
LOGGED_ON_USER=200
OWNER=300


class Language(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    descr = models.CharField(max_length=63)

    def __unicode__(self):
        return self.id

    @classmethod
    def get_default(cls):
        return cls.objects.get(id=settings.ZADIG_LANGUAGES[0][0])

    class Meta:
        db_table = 'zadig_language'


class Permission(models.Model):
    descr = models.CharField(max_length=31)

    def __unicode__(self):
        return self.descr

    class Meta:
        db_table = 'zadig_permission'


class Lentity(models.Model):
    user = models.ForeignKey(User, null=True)
    group = models.ForeignKey(Group, null=True)
    special = models.PositiveSmallIntegerField(null=True)

    def __unicode__(self):
        return "user=%s, group=%s, special=%d" % (str(self.user),
                                                str(self.group), self.special)

    def includes(self, user, entry=None):
        # Case self.user is not null
        if self.user:
            return self.user==user

        # Case self.group is not null
        if self.group:
            return self.group in user.groups.all()

        # Case self.special is not null
        if self.special==EVERYONE:
            return True
        if self.special==LOGGED_ON_USER:
            return user.username == entry.request.user.username
        if self.special==OWNER:
            return entry and entry.owner==user
        if self.special in (PERM_VIEW, PERM_EDIT, PERM_ADMIN, PERM_DELETE,
                                                                PERM_SEARCH):
            return entry and self.special in entry.permissions

        # Should never reach here
        assert(False)

    class Meta:
        unique_together = ('user', 'group')
        db_table = "zadig_lentity"

    def save(self, force_insert=False, force_update=False):
        """Verify integrity before saving."""
        if (not self.user and not self.group and self.special in
                    (EVERYONE, LOGGED_ON_USER, OWNER, PERM_VIEW, PERM_EDIT,
                    PERM_ADMIN, PERM_DELETE, PERM_SEARCH)) \
                    or (self.user and not self.group and not self.special) \
                    or (not self.user and self.group and not self.special):
            return super(Lentity, self).save(force_insert, force_update)
        raise Exception("Invalid Lentity: " + self.__unicode__())


class State(models.Model):
    descr = models.CharField(max_length=31)

    def __unicode__(self):
        return self.descr

    class Meta:
        db_table = 'zadig_state'


class StatePermission(models.Model):
    state = models.ForeignKey(State)
    lentity = models.ForeignKey(Lentity)
    permission = models.ForeignKey(Permission)

    def __unicode__(self):
        return "state=%s, %s, permission=%s" % (self.state.descr, self.lentity,
                                                            self.permission)
    class Meta:
        db_table = 'zadig_statepermission'


class StateTransition(models.Model):
    source_state = models.ForeignKey(State, related_name='source_rules')
    target_state = models.ForeignKey(State, related_name='target_rules')
    lentity = models.ForeignKey(Lentity,
                                default=Lentity.objects.get(special=OWNER))

    def __unicode__(self):
        return "%s => %s (%s)" % (self.source_state, self.target_state,
                                                                self.lentity)

    class Meta:
        db_table = 'zadig_statetransition'


class Workflow(models.Model):
    name = models.CharField(max_length=127, unique=True)
    states = models.ManyToManyField(State)
    state_transitions = models.ManyToManyField(StateTransition)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'zadig_workflow'


class MultilingualGroup(models.Model):

    def check(self):
        entries = list(self.entry_set.all())
        if len(entries)<2:
            self.delete()
        languages_in_group = set()
        for entry in entries:
            latest_vobject = entry.vobject_set.order_by('-version_number')[0]
            if not latest_vobject.language:
                raise IntegrityError(_(u"The MultilingualGroup (id=%d) "
                    "contains Entry (id=%d) which does not have a language") %
                    (self.id, entry.id))
            if latest_vobject.language.id in languages_in_group:
                raise IntegrityError(_(u"The MultilingualGroup (id=%d) "
                    "contains multiple occurrences of language %s (the "
                    "entries are %s)") % (self.id, latest_vobject.language.id,
                    ', '.join([str(x) for x in entries])))
            languages_in_group.add(latest_vobject.language.id)

    def delete(self, *args, **kwargs):
        """This should work like ON CASCADE SET NULL, it should not delete
        any entries!"""
        for e in self.entry_set.all():
            e.multilingual_group = None
            e.save()
        return super(MultilingualGroup, self).delete(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.id)

    class Meta:
        db_table = 'zadig_multilingualgroup'


def _check_multilingual_group(request, mgid):
    """Called whenever one needs to verify the integrity of specified
    multilingual group. What it actually does is postpone this check for
    commit time (the middleware makes the check)."""
    if not 'multilingual_groups_to_check' in request.__dict__:
        request.multilingual_groups_to_check = set()
    request.multilingual_groups_to_check.add(mgid)


class EntryManager(models.Manager):

    def get_by_path(self, request, path):
        entry = None
        for name in utils.split_path(path):
            entry = get_object_or_404(self, name=name, container=entry)
            entry.request = request
            if not PERM_VIEW in entry.permissions:
                raise Http404
        return entry

class Entry(models.Model):
    object_class = models.CharField(max_length=100)
    container = models.ForeignKey('self', related_name="all_subentries",
                                  blank=True, null=True)
    name = models.SlugField(max_length=100, blank=True)
    seq = models.PositiveIntegerField()
    owner = models.ForeignKey(User)
    state = models.ForeignKey(State)
    multilingual_group = models.ForeignKey(MultilingualGroup, blank=True,
                                                                null=True)
    btemplate = models.CharField(max_length=100, blank=True)
    objects = EntryManager()

    edit_template_name = 'edit_entry.html'

    def __init__(self, *args, **kwargs):
        # If called with only two arguments, then it is someone calling the
        # Zadig API, and the two arguments are request and path.
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
            self.__initialize()
        if not self.object_class:
            self.object_class = self._meta.object_name

    def __initialize(self):
        """Set all other attributes of a newly created Entry, when only
        container has been set."""
        if not PERM_EDIT in self.rcontainer.permissions:
            raise PermissionDenied(_(u"Permission denied"))
        self.seq = 1
        siblings = Entry.objects.filter(container=self.rcontainer)
        if siblings.count():
            self.seq = siblings.order_by('-seq')[0].seq + 1
        self.owner = self.request.user
        self.state = Workflow.objects.get(id=settings.WORKFLOW_ID) \
            .state_transitions \
            .get(source_state__descr="Nonexistent").target_state

    @property
    def absolute_uri(self):
        return self.request.build_absolute_uri(self.spath)

    def can_contain(self, cls):
        return PERM_EDIT in self.permissions

    @classmethod
    def can_be_contained(cls, parent):
        return parent.can_contain(cls)
        
    def save(self, *args, **kwargs):
        if self.multilingual_group:
            _check_multilingual_group(self.request, self.multilingual_group.id)
        # If this is an update, also check the multilingual group to which 
        # this entry originally belonged. FIXME: This solution is a bit ugly;
        # check http://stackoverflow.com/questions/2029814/keeping-track-of-changes-since-the-last-save-in-django-models
        if self.id:
            original_mg = Entry.objects.get(id=self.id).multilingual_group
            if original_mg and self.request:
                _check_multilingual_group(self.request, original_mg.id)
        return super(Entry, self).save(args, kwargs)

    def __renumber_subentries(self):
        for i, s in enumerate(self.all_subentries.all()):
            if s.seq != i+1:
                s.seq = i+1
                s.request = self.request
                s.save()

    def delete(self, *args, **kwargs):
        """Several things need to be done: check that the user has permission
        to delete, check that we are not deleting the root page, cleanup
        multilingual group, cleanup sequence number. We check for permission
        only if we have a request attribute. If we don't have a request
        attribute, it means that it is likely Django calling us, for example in
        order to cascade delete, which means we should do it even without
        permission (hopefully, that is)."""
        if 'request' in self.__dict__ and PERM_DELETE not in self.permissions:
            raise PermissionDenied(_(u"Permission denied"))
        container = self.rcontainer
        if not container:
            raise PermissionDenied(_(u"The root object cannot be deleted"))
        mg = self.multilingual_group
        result = super(Entry, self).delete(*args, **kwargs)
        if mg: _check_multilingual_group(self.request, mg.id)
        container.__renumber_subentries()
        return result

    @property
    def ownername(self):
        result = self.owner.get_full_name()
        if not result.strip():
            result = self.owner.username
        return result

    @property
    def creation_date(self):
        return self.vobject_set.order_by('version_number')[0].date

    @property
    def last_modification_date(self):
        return self.vobject.date

    @property
    def rcontainer(self):
        result = self.container
        if result:
            result.request = self.request
        return result

    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        cls = [x for x in entry_types if x.__name__==self.object_class][0]
        hierarchy = []
        while cls!=type(self):
            hierarchy.insert(0, cls)
            cls = cls.__bases__[0]
        result = self
        for a in hierarchy:
            result = getattr(result, a.__name__.lower())
        result.request = self.request
        return result

    @property
    def permissions(self):
        if self.request.user.is_authenticated() and (self.owner.pk ==
                    self.request.user.pk or self.request.user.is_superuser):
            return set((PERM_VIEW, PERM_EDIT, PERM_ADMIN, PERM_DELETE,
                                                                PERM_SEARCH))
        result = set()
        if self.request.user.is_authenticated():
            lentities = [Lentity.objects.get(user=self.request.user),
                         Lentity.objects.get(special=EVERYONE),
                         Lentity.objects.get(special=LOGGED_ON_USER)]
            lentities.append(Lentity.objects.filter(
                                  group__in=self.request.user.groups.all()))
        else:
            lentities = [Lentity.objects.get(special=EVERYONE)]
        for lentity in lentities:
            for perm in EntryPermission.objects.filter(lentity=lentity,
                                                              entry=self):
                result.add(perm.permission_id)
            for perm in StatePermission.objects.filter(lentity=lentity,
                                                              state=self.state):
                result.add(perm.permission_id)
        return result

    @property
    def touchable(self):
        return self.permissions.intersection(set((PERM_EDIT, PERM_ADMIN))
                                                                    ) != set()

    @property
    def vobject(self):
        return self.get_vobject()

    def get_vobject(self, version_number=None):
        latest_vobject = self.vobject_set.order_by('-version_number')[0]
        if version_number is None:
            vobject = latest_vobject
        else:
            vobject = self.vobject_set.get(version_number=version_number)
        if vobject.version_number != latest_vobject.version_number \
                and PERM_EDIT not in self.permissions:
            raise PermissionDenied(_(u"Permission denied"))
        vobject.request = self.request
        return vobject.descendant

    @property
    def path(self):
        result = self.name
        entry = self
        while entry.rcontainer and entry.rcontainer.name:
            entry = entry.rcontainer
            result = entry.name + '/' + result
        return result

    @property
    def spath(self):
        result = '/' + self.path + '/'
        if result == '//':
            result = '/'
        return result

    @property
    def type(self):
        return self.descendant.__class__.__name__

    @property
    def base_template(self):
        if self.btemplate: return self.btemplate
        if self.container: return self.rcontainer.base_template
        return 'base.html'

    def contains(self, entry):
        while entry:
            if entry.rcontainer == self: return True
            entry = entry.rcontainer
        return False

    @property
    def subentries(self):
        parent_permissions = self.permissions
        if PERM_VIEW not in parent_permissions:
            raise PermissionDenied(_(u"Permission denied"))
        subentries = list(self.all_subentries.order_by('seq').all())
        for s in subentries:
            s.request = self.request
        if PERM_EDIT in parent_permissions:
            return subentries
        result = []
        for s in subentries:
            if PERM_SEARCH in s.permissions:
                result.append(s)
        return result

    def reorder(self, source_seq, target_seq):
        if PERM_EDIT not in self.permissions:
            raise PermissionDenied(_(u"Permission denied"))
        subentries = self.all_subentries.order_by('seq').all()
        for s in subentries: s.request = self.request
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

    __langs = [x[0] for x in settings.ZADIG_LANGUAGES]
    @property
    def alt_lang_entries(self):
        def cmp(x, y):
            xi = self.__langs.index(x.vobject.language.id)
            yi = self.__langs.index(y.vobject.language.id)
            return yi-xi
        if not self.multilingual_group:
            return []
        result = list(self.multilingual_group.entry_set.all())
        for x in result:
            if x.id == self.id:
                result.remove(x)
                break
        result.sort(cmp)
        return result

    def __create_metatags_formset(self, new):
        """Return a formset of metatags forms, as many as existing metatag sets
        plus one if there is another available language. Called by edit_view()
        method. """
        initial = []
        if new:
            vobject = self.rcontainer.vobject.descendant
            lang = vobject.language or Language.get_default()
            initial.append({ 'language': lang.id })
        else:
            vobject = self.vobject.descendant
            used_langs = []
            for m in vobject.metatags.all():
                initial.append({'language': m.language.id, 'title': m.title,
                    'short_title': m.short_title, 'description': m.description})
                used_langs.append(m.language.id)
            remaining_langs = set(self.__langs).difference(used_langs)
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

    def set_altlang(self, altlang):
        mg = self.multilingual_group
        if not altlang:
            self.multilingual_group = None
            if mg: _check_multilingual_group(self.request, mg.id)
            return
        try:
            e = Entry.objects.get_by_path(self.request, altlang)
        except Http404:
            _check_multilingual_group(self.request, mg.id)
            return
        if not self.vobject.language:
            raise IntegrityError(_(
                u'self.vobject does not have a language specified'))
        if not e.vobject.language:
            raise IntegrityError(_(
                u'The altlang vobject does not have a language specified'))
        if self.vobject.language.id == e.vobject.language.id:
            raise IntegrityError(_(u'The two objects are in the same language'))
        if e.multilingual_group:
            self.multilingual_group = e.multilingual_group
        else:
            amultilingual_group = MultilingualGroup()
            amultilingual_group.save()
            self.multilingual_group = amultilingual_group
            e.multilingual_group = amultilingual_group
            e.save()

    def edit_subform(self, data=None, files=None, new=False):
        return forms.Form(data, files)

    def process_edit_subform(self, vobject, form): pass

    def edit_view(self, new=False, parms=None):
        if (new and not self.rcontainer.touchable) or (
                                            not new and not self.touchable):
            raise Http404
        if self.request.method != 'POST':
            mainform = EditEntryForm(initial={ 'name': self.name,
                        'language': self.vobject.language if not new else '',
                        'altlang': self.alt_lang_entries[0].spath
                            if self.alt_lang_entries else '',
                        })
            metatagsformset = self.__create_metatags_formset(new)
            subform = self.edit_subform(new=new)
            optionsforms = []
            for o in entry_option_sets:
                oset = o(entry=self) if new else \
                                        o.objects.get_or_create(entry=self)[0]
                optionsforms.append(oset.get_form_from_data())
        else:
            mainform = EditEntryForm(self.request.POST, request=self.request,
                            entry=self.container if new else self, new=new)
            metatagsformset = MetatagsFormSet(self.request.POST)
            subform = self.edit_subform(data=self.request.POST,
                                        files=self.request.FILES, new=new)
            optionsforms = [o.form(self.request.POST)
                                                    for o in entry_option_sets]
            all_forms_are_valid = all(
                [mainform.is_valid(),
                 metatagsformset.is_valid(),
                 subform.is_valid() ] +
                [o.is_valid() for o in optionsforms])
            if all_forms_are_valid:
                if new:
                    self.__initialize()
                    self.name = mainform.cleaned_data['name']
                self.set_altlang(mainform.cleaned_data['altlang'])
                self.save()
                lang_id = mainform.cleaned_data['language']
                nvobject = self.vobject_class(entry=self,
                    version_number=new and 1 or (
                                            self.vobject.version_number + 1),
                    language=Language.objects.get(id=lang_id) if lang_id else
                                                                        None)
                nvobject.request = self.request
                self.process_edit_subform(nvobject, subform)
                nvobject.save()
                self.__process_metatags_formset(nvobject, metatagsformset)
                for o,f in map(lambda x,y:(x,y), entry_option_sets,
                                                                 optionsforms):
                    option_set = o.objects.get_or_create(entry=self)[0]
                    option_set.set_data_from_form(f)
                    option_set.save()
                if mainform.cleaned_data['name'] != self.name:
                    self.rename(mainform.cleaned_data['name'])
                return HttpResponseRedirect(self.spath+'__info__/')
        if new:
            vobject = self.rcontainer.vobject
        else:
            vobject = self.vobject
        return render_to_response(self.edit_template_name,
              { 'vobject': vobject,
                'mainform': mainform, 'metatagsformset': metatagsformset,
                'subform': subform, 'optionsforms': optionsforms },
                context_instance = RequestContext(self.request))

    def rename(self, newname):
        if not self.rcontainer:
            raise ValueError(_("The root page cannot be renamed"))
        for sibling in self.container.all_subentries.all():
            if sibling.id == self.id: continue
            if sibling.name == newname:
                raise ValueError(_("Cannot rename; target name already exists"))
        oldname = self.name
        self.name = newname
        self.save()
        # I'm not particularly happy about importing something from
        # zstandard; in theory we don't know about it in the core.
        from zadig.zstandard.models import InternalRedirectionEntry, \
                                                VInternalRedirection
        nentry = InternalRedirectionEntry(container=self.rcontainer)
        nentry.request = self.request
        nentry.__initialize()
        nentry.name = oldname
        nentry.save()
        nvobject = VInternalRedirection(entry=nentry,
            version_number=1,
            language=self.vobject.language,
            target=self)
        nvobject.save()
        nmetatags = VObjectMetatags(
            vobject=nvobject,
            language=Language.get_default(),
            title=_("Redirection"))
        nmetatags.save()

    def move(self, target_entry):
        if 'request' not in target_entry.__dict__:
            target_entry.request = self.request
        if not self.rcontainer:
            raise ValueError(_("The root page cannot be moved"))
        if self.rcontainer.id == target_entry.id:
            return
        for nsibling in target_entry.all_subentries.all():
            if nsibling.name == self.name:
                raise ValueError(_("Cannot move; an entry with the same name at the target location already exists"))
        if (PERM_EDIT not in target_entry.permissions) \
                                    or (PERM_DELETE not in self.permissions):
            raise PermissionDenied(_("Permission denied"))
        oldcontainer = self.rcontainer
        oldseq = self.seq
        self.seq = target_entry.all_subentries.count() + 1
        self.container = target_entry
        self.save()
        # I'm not particularly happy about importing something from
        # zstandard; in theory we don't know about it in the core.
        from zadig.zstandard.models import InternalRedirectionEntry, \
                                                VInternalRedirection
        nentry = InternalRedirectionEntry(container=oldcontainer)
        nentry.request = self.request
        nentry.__initialize()
        nentry.seq = oldseq
        nentry.name = self.name
        nentry.save()
        nvobject = VInternalRedirection(entry=nentry,
            version_number=1,
            language=self.vobject.language,
            target=self)
        nvobject.save()
        nmetatags = VObjectMetatags(
            vobject=nvobject,
            language=Language.get_default(),
            title=_("Redirection"))
        nmetatags.save()

    def contents_view(self, parms=None):
        subentries = self.subentries
        vobject = self.vobject
        if self.request.method == 'POST' and 'move' in self.request.POST:
            move_item_form = MoveItemForm(self.request.POST)
            if move_item_form.is_valid():
                s = move_item_form.cleaned_data['move_object']
                t = move_item_form.cleaned_data['before_object']
                self.reorder(s, t)
                subentries = self.subentries
        elif self.request.method == 'POST' and 'cut' in self.request.POST:
            formset = ContentsFormSet(self.request.POST)
            self.request.session['cut_entries'] = []
            for i,f in enumerate(formset.cleaned_data):
                if f['select_object']:
                    self.request.session['cut_entries'].append(subentries[i].id)
        items_formset = ContentsFormSet(initial=[
            { 'entry_id': x.id,
              'select_object': x.id in self.request.session.get(
                                                            'cut_entries', [])
            } for x in subentries ])
        move_item_form = MoveItemForm(initial=
                {'num_of_objects': len(subentries)})
        return render_to_response('entry_contents.html',
                { 'vobject': vobject, 'subentries': subentries,
                  'formset': items_formset,
                  'subentries_with_formset': map(lambda x,y: (x,y), subentries,
                                                        items_formset.forms),
                  'move_item_form': move_item_form},
                context_instance = RequestContext(self.request))

    def history_view(self, parms=None):
        vobject = self.vobject
        return render_to_response('entry_history.html', { 'vobject': vobject },
                context_instance = RequestContext(self.request))

    def __change_owner(self, new_owner, recursive):

        if self.request.user != self.owner and \
                                        not self.request.user.is_superuser:
            raise PermissionDenied(_(u"Permission denied"))
        if new_owner != self.owner:
            self.owner = new_owner
            self.save()
        if recursive:
            for e in self.subentries:
                e.__change_owner(new_owner, recursive)

    def permissions_view(self, parms=None):
        vobject = self.vobject
        if self.request.method != 'POST':
            permissions_form = EntryPermissionsForm({ 'owner': self.owner })
        else:
            permissions_form = EntryPermissionsForm(self.request.POST)
            if permissions_form.is_valid():
                new_owner = User.objects.get(username=
                                permissions_form.cleaned_data['owner'])
                recursive = permissions_form.cleaned_data['recursive']
                self.__change_owner(new_owner, recursive)
        return render_to_response('entry_permissions.html',
                { 'vobject': vobject,'permissions_form': permissions_form },
                context_instance = RequestContext(self.request))

    def undelete(self):
        ver = self.vobject.version_number
        assert(ver>1)
        old_vobject = self.get_vobject(ver-1).descendant
        assert(not old_vobject.deletion_mark)
        nvobject = old_vobject.duplicate()
        nvobject.request = self.request
        nvobject.request.view_name = 'info'
        return nvobject.descendant.info_view()

    @property
    def possible_target_states(self):
        workflow = Workflow.objects.get(id=settings.WORKFLOW_ID)
        result = []
        for transition in self.state.source_rules.all():
            if workflow in transition.workflow_set.all() and \
                    transition.lentity.includes(self.request.user, entry=self):
                result.append(transition.target_state)
        return result
        
    def __unicode__(self):
        result = self.name
        container = self.rcontainer
        while container:
            result = container.name + '/' + result
            container = container.rcontainer
        return result

    class Meta:
        unique_together = (('container', 'name'),
                           ('container', 'seq'))
        db_table = 'zadig_entry'
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
        db_table = 'zadig_entrypermission'


class VObjectManager(models.Manager):

    def get_by_path(self, request, path, version_number=None):
        entry = Entry.objects.get_by_path(request, path)
        return entry.get_vobject(version_number)


class VObject(models.Model):
    object_class = models.CharField(max_length=100)
    entry = models.ForeignKey(Entry, related_name="vobject_set")
    version_number = models.PositiveIntegerField()
    date = models.DateTimeField()
    language = models.ForeignKey(Language, blank=True, null=True)
    deletion_mark = models.BooleanField(default=False)
    objects = VObjectManager()

    def __init__(self, *args, **kwargs):
        result = super(VObject, self).__init__(*args, **kwargs)
        self.request = None
        if not self.object_class:
            self.object_class = self._meta.object_name

    def save(self, *args, **kwargs):
        from datetime import datetime
        if self.entry.multilingual_group:
            _check_multilingual_group(self.request,
                                            self.entry.multilingual_group.id)
        if not self.date:
            self.date = datetime.now()
        return super(VObject, self).save(args, kwargs)

    @property
    def descendant(self):
        if self._meta.object_name == self.object_class:
            return self
        cls = [x.vobject_class for x in entry_types
                            if x.vobject_class.__name__==self.object_class][0]
        hierarchy = []
        while cls!=type(self):
            hierarchy.insert(0, cls)
            cls = cls.__bases__[0]
        result = self
        for a in hierarchy:
            result = getattr(result, a.__name__.lower())
        result.request = self.request
        return result

    @property
    def rentry(self):
        entry = self.entry
        entry.request = self.request
        return entry

    @property
    def metatags(self):
        result = self.metatags_set
        if 'request' in self.__dict__:
            result.request = self.request
        return result

    def view_deleted(self, parms):
        assert(self.deletion_mark)
        if self.request.view_name=='info':
            return render_to_response('view_deleted_entry.html',
                { 'vobject': self, },
                context_instance = RequestContext(self.request))
        if self.request.view_name=='history':
            return self.rentry.history_view()
        if self.request.view_name=='undelete':
            return self.rentry.undelete()
        raise Http404

    def duplicate(self):
        """Originally downloaded from http://djangosnippets.org/snippets/1282/
        and then modified.
        Copyright (C) 2009 by djangosnippets user johnboxall
        Copyright (C) 2010 National Technical University of Athens"""
        from django.db.models.query import CollectedObjects
        from django.db.models.fields.related import ForeignKey
        from datetime import datetime
        ndate = datetime.now()
        nversion_number = self.entry.vobject_set.order_by(
                                    '-version_number')[0].version_number + 1
        collected_objs = CollectedObjects()
        self.descendant._collect_sub_objects(collected_objs)
        related_models = collected_objs.keys()
        root_obj = None
        # Traverse the related models in reverse deletion order.    
        for model in reversed(related_models):
            # Find all FKs on `model` that point to a `related_model`.
            fks = []
            for f in model._meta.fields:
                if isinstance(f, ForeignKey) and f.rel.to in related_models:
                    fks.append(f)
            # Replace each `sub_obj` with a duplicate.
            sub_obj = collected_objs[model]
            for pk_val, obj in sub_obj.iteritems():
                for fk in fks:
                    fk_value = getattr(obj, "%s_id" % fk.name)
                    # If this FK has been duplicated then point to the
                    # duplicate.
                    if fk_value in collected_objs[fk.rel.to]:
                        dupe_obj = collected_objs[fk.rel.to][fk_value]
                        setattr(obj, fk.name, dupe_obj)
                # Duplicate the object and save it.
                obj.id = None
                if isinstance(obj, VObject):
                    obj.date = ndate
                    obj.version_number = nversion_number
                if root_obj is None:
                    root_obj = obj
                obj.save()
        return root_obj

    def __unicode__(self):
        return '%s v. %d, id=%d' % (self.entry.__unicode__(),
                self.version_number, self.id)

    class Meta:
        ordering = ('entry', 'version_number')
        unique_together = ('entry', 'version_number')
        db_table = 'zadig_vobject'
        permissions = (("view", "View"),)


class MetatagManager(models.Manager):

    @property
    def default(self):
        first_metatags = self.all()[0]
        language = None
        if 'request' in self.__dict__ and self.request:
            language = self.request.effective_language
            a = self.filter(language=language)
            if a: return a[0]
        language = first_metatags.vobject.language
        a = self.filter(language=language)
        if a: return a[0]
        return first_metatags


class VObjectMetatags(models.Model):
    vobject = models.ForeignKey(VObject, related_name='metatags_set')
    language = models.ForeignKey(Language)
    title = models.CharField(max_length=250)
    short_title = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    objects = MetatagManager()

    def __unicode(self):
        return '%s %s metatags' % (self.vobject.__unicode__(),
                                   self.language)

    def get_short_title(self):
        return self.short_title or self.title

    class Meta:
        unique_together = ('vobject', 'language')
        db_table = 'zadig_vobjectmetatags'


class EditEntryForm(forms.Form):
    language = forms.ChoiceField(choices=[('','')] +
                            list(settings.ZADIG_LANGUAGES), required=False)
    name = forms.CharField(required=False,
                        max_length=Entry._meta.get_field('name').max_length)
    altlang = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """We keep a pointer to 'request' and 'entry' if the caller supplies
        it, in order to use it when we clean."""
        if 'request' in kwargs:
            self.request = kwargs['request']
            del(kwargs['request'])
            self.entry = kwargs['entry']
            del(kwargs['entry'])
            self.new = kwargs['new']
            del(kwargs['new'])
        super(EditEntryForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        n = self.cleaned_data['name']
        if (self.new and self.entry.all_subentries.filter(name=n).count()) or (
                not self.new and self.entry.name!=n and
                self.entry.container.all_subentries.filter(name=n).count()):
            raise forms.ValidationError(_(u"An object with this name "
                "already exists; choose another name."))
        return n

    def clean(self):
        c = self.cleaned_data
        c['altlang'] = c['altlang'].strip()
        if c['altlang']:
            if not c['language']:
                raise forms.ValidationError(_(u"Specify a language, or "
                    "don't specify an alternative language"))
            try:
                e = Entry.objects.get_by_path(self.request, c['altlang'])
            except Http404:
                raise forms.ValidationError(_(u"The object specified as "
                    "alternative language does not exist, or you do not have "
                    "permission to view it."))
            if not self.new and e.id==self.entry.id:
                raise forms.ValidationError(_(u"Specify a different object "
                    "as alternative language, not this object."))
            if not e.vobject.language:
                raise forms.ValidationError(_(u"The object you specified as "
                    "alternative language does not have a language defined."))
            if e.vobject.language.id==c['language']:
                raise forms.ValidationError(_(u"The object you specified as "
                    "alternative language has the same language as this "
                    "object"))
        return c


class EntryPermissionsForm(forms.Form):
    owner = forms.CharField(required=True, max_length=50)
    recursive = forms.BooleanField(required=False)
    def clean(self):
        c = self.cleaned_data
        c['owner'] = c['owner'].strip()
        if User.objects.filter(username=c['owner']).count()==0:
            raise forms.ValidationError(_(u"Nonexistent user"))
        return c


class MetatagsForm(forms.Form):
    language = forms.ChoiceField(settings.ZADIG_LANGUAGES)
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


class ContentsItemForm(forms.Form):
    select_object = forms.BooleanField(required=False)

ContentsFormSet = formset_factory(ContentsItemForm, extra=0)



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
