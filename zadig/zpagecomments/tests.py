from django.test import TestCase
from zadig.zpagecomments.models import PageComment


class TestZpagecomments(TestCase):
    fixtures = ['testdata.json']
    test_comment_postdata = {'action': 'zpagecomments.add_comment',
            'commenter_name': 'John Commenter',
            'commenter_email': 'john@commenter.example.com',
            'commenter_website': 'http://commenter.example/john',
            'comment': '<p>Hello, world!</p>'}


    def test_submit_comment(self):
        # Try to submit a comment when comments are not allowed
        response = self.client.post('/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 404)

        # Now enable comments
        response = self.client.post('/', { 'action': 'login',
                                'username': 'admin', 'password': 'secret0' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/', { 'action': 'edit',
                      'name': '', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Home',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 302)

        # This time we should succeed
        response = self.client.post('/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 302)

        self.client.logout()

    def test_change_comment_state(self):
        # Submit a comment
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/', { 'action': 'edit',
                      'name': '', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Home',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 302)
        self.client.logout()
        response = self.client.post('/', self.test_comment_postdata)
        self.assertEquals(response.status_code, 302)

        # Try to change comment state while logged out
        comment = PageComment.objects.get()
        response = self.client.post('/', {
            'action': 'zpagecomments.change_comment_state', 'comment_id': comment.id,
            'new_state': 'DELETED' })
        self.assertEquals(response.status_code, 404)

        # Try the same thing, logged in
        self.client.login(username='admin', password='secret0')
        comment = PageComment.objects.all()[0]
        response = self.client.post('/', {
            'action': 'zpagecomments.change_comment_state', 'comment_id': comment.id,
            'new_state': 'DELETED' })
        self.assertEquals(response.status_code, 302)
