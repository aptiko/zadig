from datetime import datetime, timedelta

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import User
import settings

from zadig.core.models import Entry
from zadig.core.utils import set_request
from zadig.zpagecomments.models import PageComment


class TestZpagecomments(TestCase):
    fixtures = ['testdata.json']
    test_comment_postdata = {'action': 'zpagecomments.edit_comment',
            'comment_id': '',
            'commenter_name': 'John Commenter',
            'commenter_email': 'john@commenter.example.com',
            'commenter_website': 'http://commenter.example.com/john',
            'comment': 'Hello, world!',
            'comment_state': 'PUBLISHED',}

    def setUp(self):
        # Create a page on which we will make tests with comments
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/', { 'action': 'new',
                      'entry_type': 'Page', 'name': 'test1',
                      'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test 1',
                      'form-0-language': 'en' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/test1/', { 'action': 'change_state',
                      'state': 3 })
        self.assertEquals(response.status_code, 200) # This should be 302
        self.client.logout()

    def tearDown(self):
        request = HttpRequest()
        request.user = User.objects.get(username='admin')
        set_request(request)
        Entry.objects.get_by_path('/test1/').delete()
        set_request(None)

    def test_submit_comment(self):
        # Try to submit a comment when comments are not allowed
        response = self.client.post('/test1/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 404)

        # Now enable comments
        response = self.client.post('/test1/', { 'action': 'login',
                                'username': 'admin', 'password': 'secret0' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/test1/', { 'action': 'edit',
                      'name': 'test1', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test 1',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 302)

        # This time we should succeed
        response = self.client.post('/test1/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 302)

        self.client.logout()

    def test_change_comment_state(self):
        # Submit a comment
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/test1/', { 'action': 'edit',
                      'name': 'test1', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Home',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 302)
        self.client.logout()
        response = self.client.post('/test1/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 302)

        # Try to change comment state while logged out
        comment = PageComment.objects.get()
        response = self.client.post('/test1/', {
            'action': 'zpagecomments.change_comment_state', 'comment_id': comment.id,
            'new_state': 'DELETED' })
        self.assertEquals(response.status_code, 404)

        # Try the same thing, logged in
        self.client.login(username='admin', password='secret0')
        comment = PageComment.objects.all()[0]
        response = self.client.post('/test1/', {
            'action': 'zpagecomments.change_comment_state', 'comment_id': comment.id,
            'new_state': 'DELETED' })
        self.assertEquals(response.status_code, 302)

    def test_comments_closed(self):
        # Enable comments
        response = self.client.post('/test1/', { 'action': 'login',
                                'username': 'admin', 'password': 'secret0' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/test1/', { 'action': 'edit',
                      'name': 'test1', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test 1',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 302)
        self.client.logout()

        # Get the first vobject
        request = HttpRequest()
        request.user = User.objects.get(username='admin')
        set_request(request)
        first_vobject = Entry.objects.get_by_path('/test1/').get_vobject(1)
        set_request(None)

        creation_date = first_vobject.date
        try:
            # Change the creation_date to be sufficiently in the past
            first_vobject.date = datetime.now() - \
                        settings.ZPAGECOMMENTS_CLOSE_AFTER-timedelta(days=1)
            first_vobject.save()

            # Now try to submit a comment
            response = self.client.post('/test1/', self.test_comment_postdata)
            self.assertEquals(response.status_code, 404)
        finally:
            first_vobject.date = creation_date
            first_vobject.save()
