import unittest

from django.contrib.auth.models import User, Group
from django.http import HttpRequest

from zadig.core.models import Lentity, Entry, State, \
                    EVERYONE, LOGGED_ON_USER, OWNER, \
                    PERM_VIEW, PERM_EDIT, PERM_DELETE, PERM_ADMIN, PERM_SEARCH
from zadig.core.middleware import threadlocals


class TestPermissions(unittest.TestCase):

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
        threadlocals.request = HttpRequest()
        threadlocals.request.user = self.user1
        self.rootentry = Entry.objects.get_by_path('/')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.group1.delete()
        self.lentity1.delete()
        self.lentity2.delete()
        self.lentityg1.delete()

    def test_Lentity_includes(self):
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

    def test_Entry_possible_target_states(self):
        published = State.objects.get(descr="Published")
        private = State.objects.get(descr="Private")
        saved_owner = self.rootentry.owner
        saved_state = self.rootentry.state
        try:
            self.rootentry.state = published
            self.rootentry.owner = self.user1
            self.rootentry.save()
            target_states = self.rootentry.possible_target_states
            self.assertEqual(len(target_states), 1)
            self.assertEqual(target_states[0].descr, u"Private")
            self.rootentry.state = private
            self.rootentry.save()
            target_states = self.rootentry.possible_target_states
            self.assertEqual(len(target_states), 1)
            self.assertEqual(target_states[0].descr, u"Published")
            self.rootentry.state = published
            self.rootentry.owner = self.user2
            self.rootentry.save()
            target_states = self.rootentry.possible_target_states
            self.assertEqual(len(target_states), 0)
        finally:
            self.rootentry.owner = saved_owner
            self.rootentry.state = saved_state
            self.rootentry.save()
