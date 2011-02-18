import unittest

from django.contrib.auth.models import User, Group, AnonymousUser
from django.test.client import Client

from zadig.core.models import Lentity, Entry, State, \
                    EVERYONE, LOGGED_ON_USER, OWNER, \
                    PERM_VIEW, PERM_EDIT, PERM_DELETE, PERM_ADMIN, PERM_SEARCH


class TestPermissions(unittest.TestCase):

    def setUp(self):
        # Create two users (user1, user2) and one group (group1) containing
        # user1
        self.adminuser = User.objects.create_user('admin', 'admin@nowhere.com',
                                                            password='secret0')
        self.adminuser.is_superuser = True
        self.adminuser.save()
        self.user1 = User.objects.create_user('user1', 'user1@nowhere.com',
                                                            password='secret1')
        self.user2 = User.objects.create_user('user2', 'user2@nowhere.com',
                                                            password='secret2')
        self.group1 = Group(name='group1')
        self.group1.save()
        self.user1.groups.add(self.group1)
        self.lentity0 = Lentity(user=self.adminuser)
        self.lentity0.save()
        self.lentity1 = Lentity(user=self.user1)
        self.lentity1.save()
        self.lentity2 = Lentity(user=self.user2)
        self.lentity2.save()
        self.lentityg1 = Lentity(group=self.group1)
        self.lentityg1.save()

        # Nick for root entry
        self.rootentry = Entry.objects.get_by_path('/')

        # Let's put in some subentries
        self.client = Client()
        self.client.login(username='admin', password='secret0')
        for i in range(1, 6):
            istr = ['One', 'Two', 'Three', 'Four', 'Five'][i-1]
            self.client.post('/__new__/Page/', {'name': istr.lower(),
                        'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 1,
                        'form-0-language': 'en', 'form-0-title': istr,
                        'content': 'This is page %s.' % (istr,)})
        # Let's publish 2 and 4
        published = State.objects.get(descr="Published")
        self.client.post('/two/__state__/%d/' % (published.id,))
        self.client.post('/four/__state__/%d/' % (published.id,))
        self.client.logout()

        from django.http import HttpRequest
        from zadig.core.utils import set_request
        self.request = HttpRequest()
        self.request.user = self.adminuser
        set_request(self.request)

    def tearDown(self):
        self.request.user = self.adminuser
        for e in self.rootentry.subentries: e.delete()
        self.lentity0.delete()
        self.lentity1.delete()
        self.lentity2.delete()
        self.lentityg1.delete()
        self.group1.delete()
        self.user2.delete()
        self.user1.delete()
        self.adminuser.delete()
        from zadig.core.utils import set_request
        set_request(None)
        self.request = None

    def test_Lentity_includes(self):
        self.request.user = self.user1
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
        self.assertFalse(logged_on_user.includes(self.user2,
                                                    self.rootentry))
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
            self.request.user = self.user1
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

    def test_Entry_manager_filtering(self):
        self.request.user = self.user1
        self.assertEqual(Entry.objects.count(), 6) # Five plus root entry
        self.assertEqual(set([e.spath for e in Entry.objects.all()]),
                                set((u'/', u'/one/', u'/two/', u'/three/',
                                u'/four/', u'/five/')))
        self.request.user = AnonymousUser()
        self.assertEqual(Entry.objects.count(), 3) # Only three are published
        self.assertEqual(set([e.spath for e in Entry.objects.all()]),
                                            set((u'/', u'/two/', u'/four/')))
        
    def test_Entry_subentries_filtering(self):
        self.request.user = self.user1
        self.assertEqual(self.rootentry.subentries.count(), 5)
        self.assertEqual(set([e.spath for e in self.rootentry.subentries]),
                                set((u'/one/', u'/two/', u'/three/',
                                u'/four/', u'/five/')))
        self.request.user = AnonymousUser()
        self.assertEqual(self.rootentry.subentries.count(), 2)
        self.assertEqual(set([e.spath for e in self.rootentry.subentries]),
                                            set((u'/two/', u'/four/')))
