from django.core import urlresolvers
from django.db import transaction
from django.utils.translation import ugettext as _
from cms.core import models

class permissions:
    VIEW=1
    EDIT=2
    ADMIN=3
    DELETE=4

def get_entry_by_path(site, path):
    entry=None
    for name in path.split('/'):
        entry = models.Entry.objects.get(site__name=site, name=name,
                                                    container=entry)
    return entry

def create_entry(site_name, path):
    names = path.split('/')
    parent_entry = None
    for name in names[:-1]:
        parent_entry = models.Entry.objects.get(site__name=site_name,
                                        name=name, container=parent_entry)
    site = models.Site.objects.get(name=site_name)
    siblings = models.Entry.objects.filter(container=parent_entry)
    if siblings.count():
        max_seq = siblings.order_by('-seq')[0].seq
    else:
        max_seq = 0
    # FIXME: the owner_id=1 and state_id=1 below is totally wrong
    entry = models.Entry(site=site, container=parent_entry, name=names[-1],
        owner_id=1, state_id=1, seq = max_seq+1)
    return entry

def get_vobject(site, path, version_number=None):
    entry = get_entry_by_path(site, path)
    if version_number is None:
        vobject = entry.vobject_set.latest()
    else:
        vobject = entry.vobject_set.get(version_number=version_number)
    return vobject

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

@transaction.commit_manually
def reorder(parent_entry, source_seq, target_seq):
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
