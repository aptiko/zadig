from django.test import TestCase
from django.test.client import Client


class TestZstandard(TestCase):
    fixtures = ['testdata.json']

    def test_create_page(self):
        from zadig.core import models
        response = self.client.post('/__login__/',
                            { 'username': 'admin', 'password': 'secret0' })
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        response = self.client.post('/__new__/Page/',
                    { 'name': 'testpage', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test Page',
                      'form-0-language': 'en' })
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 200)
        self.client.logout()

    def test_undelete(self):
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/__new__/Page/',
                    { 'name': 'testpage', 'form-TOTAL_FORMS': 1,
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test Page',
                      'form-0-language': 'en' })
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/testpage/__state__/3/') # publish
        self.assertEquals(response.status_code, 200)
        response = self.client.post('/testpage/__delete__/')
        self.assertEquals(response.status_code, 200)

        # Try to view deleted anonymously - should fail
        self.client.logout()
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 404)

        # Try to view deleted as admin - should succeed
        self.client.login(username='admin', password='secret0')
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 200)

        # Try to undelete anonymously - should fail
        self.client.logout()
        response = self.client.post('/testpage/__undelete__/')
        self.assertEquals(response.status_code, 404)

        # Try to undelete as admin - should succeed
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/testpage/__undelete__/')
        self.assertEquals(response.status_code, 200)

        # Try to view anonymously - should succeed
        self.client.logout()
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 200)
