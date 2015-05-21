import os

from django.test import TestCase


class TestZstandard(TestCase):
    fixtures = ['testdata.json']

    def test_create_page(self):
        response = self.client.post('/', {'action': 'login',
                                          'username': 'admin',
                                          'password': 'secret0'})
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        response = self.client.post('/',
                                    {'action': 'new',
                                     'entry_type': 'Page',
                                     'name': 'testpage',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 1,
                                     'form-0-title': 'Test Page',
                                     'form-0-language': 'en'})
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 200)
        self.client.logout()

    def test_view_resized_image(self):
        response = self.client.post('/',
                                    {'action': 'login',
                                     'username': 'admin',
                                     'password': 'secret0'})
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        with open(os.path.join(os.path.dirname(__file__), 'dummy.png')) as f:
            response = self.client.post('/',
                                        {'action': 'new',
                                         'entry_type': 'Image',
                                         'name': 'testimage',
                                         'form-TOTAL_FORMS': 1,
                                         'form-INITIAL_FORMS': 1,
                                         'form-0-title': 'Test Image',
                                         'form-0-language': 'en',
                                         'content': f})
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/testimage/__resized__/1/')
        self.assertEquals(response.status_code, 200)
        self.client.logout()

    def test_undelete(self):
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/',
                                    {'action': 'new',
                                     'entry_type': 'Page',
                                     'name': 'testpage',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 1,
                                     'form-0-title': 'Test Page',
                                     'form-0-language': 'en'})
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/testpage/',
                                    {'action': 'change_state',
                                     'state': '3'})  # publish
        self.assertEquals(response.status_code, 200)
        response = self.client.post('/testpage/', {'action': 'delete'})
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
        response = self.client.post('/testpage/', {'action': 'undelete'})
        self.assertEquals(response.status_code, 404)

        # Try to undelete as admin - should succeed
        self.client.login(username='admin', password='secret0')
        response = self.client.post('/testpage/', {'action': 'undelete'})
        self.assertEquals(response.status_code, 200)

        # Try to view anonymously - should succeed
        self.client.logout()
        response = self.client.get('/testpage/')
        self.assertEquals(response.status_code, 200)
