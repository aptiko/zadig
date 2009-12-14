from django.core import urlresolvers
from django.db import transaction
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from cms.core import models
import settings

class permissions:
    VIEW=1
    EDIT=2
    ADMIN=3
    DELETE=4
    SEARCH=5

def get_entry_permissions(request, entry):
    if entry.owner.id == request.user.id:
        return set((permissions.VIEW, permissions.EDIT, permissions.ADMIN,
            permissions.DELETE, permissions.SEARCH))
    result = set()
    if request.user.is_authenticated():
        lentities = [models.Lentity.objects.get(user=request.user),
                     models.Lentity.objects.get(special=2)]
        lentities.append(models.Lentity.objects.filter(
                                        group__in=request.user.groups))
    else:
        lentities = [models.Lentity.objects.get(special=1)]
    for lentity in lentities:
        for perm in models.EntryPermission.objects.filter(lentity=lentity,
                                                            entry=entry):
            result.add(perm.permission_id)
        for perm in models.StatePermission.objects.filter(lentity=lentity,
                                                            state=entry.state):
            result.add(perm.permission_id)
    return result

def get_entry_by_path(request, site, path):
    entry=None
    for name in path.split('/'):
        entry = models.Entry.objects.get(site__name=site, name=name,
                                                    container=entry)
    if not permissions.VIEW in get_entry_permissions(request, entry):
        entry = None
    return entry

def create_entry(request, site_name, path):
    names = path.split('/')
    parent_path = '/'.join(names[:-1])
    parent_entry = get_entry_by_path(request, site_name, parent_path)
    if not permissions.EDIT in get_entry_permissions(request, parent_entry):
        raise PermissionDenied(_(u"Permission denied"))
    site = models.Site.objects.get(name=site_name)
    siblings = models.Entry.objects.filter(container=parent_entry)
    if siblings.count():
        max_seq = siblings.order_by('-seq')[0].seq
    else:
        max_seq = 0
    initial_state = models.Workflow.objects.get(id=settings.WORKFLOW_ID) \
        .state_transitions.get(source_state__descr="Nonexistent").target_state
    entry = models.Entry(site=site, container=parent_entry, name=names[-1],
        owner=request.user, state=initial_state, seq = max_seq+1)
    return entry

def get_entry_vobject(request, entry, version_number=None):
    latest_vobject = entry.vobject_set.latest()
    if version_number is None:
        vobject = latest_vobject
    else:
        vobject = entry.vobject_set.get(version_number=version_number)
    if vobject.version_number != latest_vobject.version_number \
            and permissions.EDIT not in get_entry_permissions(request, entry):
        raise PermissionDenied(_(u"Permission denied"))
    return vobject

def get_vobject(request, site, path, version_number=None):
    entry = get_entry_by_path(request, site, path)
    return get_entry_vobject(request, entry, version_number)

def get_entry_path(entry):
    result = entry.name
    while entry.container:
        entry = entry.container
        result = entry.name + '/' + result
    return result

def get_entry_url(entry):
    return urlresolvers.reverse('cms.core.views.view_object',
        kwargs = { 'site': entry.site.name, 'path': get_entry_path(entry) })

def contains(entry1, entry2):
    entry = entry2
    while entry:
        if entry.container == entry1: return True
        entry = entry.container
    return False

def get_entry_subentries(request, entry):
    parent_entry_permissions = get_entry_permissions(request, entry)
    if permissions.VIEW not in parent_entry_permissions:
        raise PermissionDenied(_(u"Permission denied"))
    subentries = entry.subentries.order_by('seq').all()
    if permissions.EDIT in parent_entry_permissions:
        return subentries
    result = []
    for s in subentries:
        if permissions.SEARCH in get_entry_permissions(request, s):
            result.append(s)
    return result

@transaction.commit_manually
def reorder(request, parent_entry, source_seq, target_seq):
    try:
        subentries = parent_entry.subentries.order_by('seq').all()
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
