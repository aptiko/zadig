import unittest

from django.contrib.auth.models import User, Group
from django.http import HttpRequest

from zadig.core.models import Lentity, Entry, \
                    EVERYONE, LOGGED_ON_USER, OWNER, \
                    PERM_VIEW, PERM_EDIT, PERM_DELETE, PERM_ADMIN, PERM_SEARCH


class TestLentity(unittest.TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@nowhere.com')
        self.user2 = User.objects.create_user('user2', 'user2@nowhere.com')
        self.group1 = Group(name='group1')
        self.group1.save()
        self.user1.groups.add(self.group1)
        self.lentity1 = Lentity(user=self.user1)
        self.lentity1.save()
        self.lentity2 = Lentity(user=self.user2)
        self.lentity2.save()
        self.lentityg1 = Lentity(group=self.group1)
        self.lentityg1.save()
        self.request = HttpRequest()
        self.request.user = self.user1
        self.rootentry = Entry.objects.get_by_path(self.request, '/')

    def test_includes(self):
        everyone = Lentity.objects.get(special=EVERYONE)
        logged_on_user = Lentity.objects.get(special=LOGGED_ON_USER)
        owner = Lentity.objects.get(special=OWNER)
        perm_view = Lentity.objects.get(special=PERM_VIEW)
        perm_edit = Lentity.objects.get(special=PERM_EDIT)
        perm_delete = Lentity.objects.get(special=PERM_DELETE)
        perm_admin = Lentity.objects.get(special=PERM_ADMIN)
        perm_search = Lentity.objects.get(special=PERM_SEARCH)
        self.assert_(self.lentity1.includes(self.user1))
        self.assertFalse(self.lentity1.includes(self.user2))
        self.assert_(self.lentityg1.includes(self.user1))
        self.assertFalse(self.lentityg1.includes(self.user2))
        self.assert_(everyone.includes(self.user1))
        self.assert_(everyone.includes(self.user2))
        self.assert_(logged_on_user.includes(self.user1, self.rootentry))
        self.assertFalse(logged_on_user.includes(self.user2, self.rootentry))
        self.assertFalse(owner.includes(self.user1))
        self.assert_(owner.includes(self.rootentry.owner, self.rootentry))
        self.assert_(perm_view.includes(self.user1, self.rootentry))
        self.assertFalse(perm_edit.includes(self.user1, self.rootentry))
        self.assertFalse(perm_delete.includes(self.user1, self.rootentry))
        self.assertFalse(perm_admin.includes(self.user1, self.rootentry))
        self.assert_(perm_search.includes(self.user1, self.rootentry))
