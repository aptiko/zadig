from django.contrib.auth.models import User, Group, AnonymousUser
from django.test import TestCase
from django.test.client import Client

from zadig.core.models import Lentity, Entry, State, \
                    EVERYONE, LOGGED_ON_USER, OWNER, \
                    PERM_VIEW, PERM_EDIT, PERM_DELETE, PERM_ADMIN, PERM_SEARCH
from zadig.core.utils import set_request


class TestPermissions(TestCase):
    fixtures = ['test.json']

    def setUp(self, *args, **kwargs):
        from django.http import HttpRequest
        self.request = HttpRequest()
        self.client = Client()

        # Some nicknames
        self.rootentry = Entry.objects.get_by_path('/')
        self.adminuser = User.objects.get(username='admin')
        self.user1 = User.objects.get(username='user1')
        self.user2 = User.objects.get(username='user2')
        self.group1 = Group.objects.get(name='group1')
        self.lentity0 = Lentity.objects.get(user=self.adminuser)
        self.lentity1 = Lentity.objects.get(user=self.user1)
        self.lentity2 = Lentity.objects.get(user=self.user2)
        self.lentityg1 = Lentity.objects.get(group=self.group1)

    def tearDown(self):
        set_request(None)
        self.request = None

    def test_Lentity_includes(self):
        self.request.user = self.user1
        set_request(self.request)
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
        set_request(self.request)
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
        set_request(self.request)
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
        set_request(self.request)
        self.assertEqual(self.rootentry.subentries.count(), 5)
        self.assertEqual(set([e.spath for e in self.rootentry.subentries]),
                                set((u'/one/', u'/two/', u'/three/',
                                u'/four/', u'/five/')))
        self.request.user = AnonymousUser()
        self.assertEqual(self.rootentry.subentries.count(), 2)
        self.assertEqual(set([e.spath for e in self.rootentry.subentries]),
                                            set((u'/two/', u'/four/')))

    def test_who_can_change_state(self):
        # Change entry 'five' to be owned by user1
        self.client.login(username='admin', password='secret0')
        self.client.logout()

        published = State.objects.get(descr="Published")
        private = State.objects.get(descr="Private")
        # User 1 should be able to change the state and back
        self.client.login(username='user1', password='secret1')
        response = self.client.post('/five/', { 'action': 'change_state',
                                        'state': str(published.id) })
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/five/', { 'action': 'change_state',
                                        'state': str(private.id) })
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        # User 2 should not
        self.client.login(username='user2', password='secret2')
        response = self.client.post('/five/', { 'action': 'change_state',
                                        'state': str(published.id) })
        self.assertEqual(response.status_code, 404)
        self.client.logout()
        # Administrator should
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/five/', { 'action': 'change_state',
                                        'state': str(published.id) })
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/five/', { 'action': 'change_state',
                                        'state': str(private.id) })
        self.assertEqual(response.status_code, 200)
        self.client.logout()
