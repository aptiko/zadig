from django.test import TestCase


class TestZpagecomments(TestCase):
    fixtures = ['testdata.json']

    def test_submit_comment(self):
        postdata = {'action': 'zpagecomments.add_comment',
            'commenter_name': 'John Commenter',
            'commenter_email': 'john@commenter.example',
            'commenter_website': 'http://commenter.example/john',
            'comment': '<p>Hello, world!</p>'}

        # Try to submit a comment when comments are not allowed
        response = self.client.post('/', postdata)
        self.assertEquals(response.status_code, 404)

        # Now enable comments
        response = self.client.post('/', { 'action': 'login',
                                'username': 'admin', 'password': 'secret0' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/', { 'action': 'edit',
                      'name': 'testpage', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test Page',
                      'form-0-language': 'en', 'allow_comments': 'on' })
        self.assertEquals(response.status_code, 200)

        # This time we should succeed
        response = self.client.post('/', postdata)
        self.assertEquals(response.status_code, 200)

        self.client.logout()
