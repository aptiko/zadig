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
                      'form-INITIAL_FORMS': 1, 'form-0-title': 'Test Page' })
        self.assertEquals(response.status_code, 200)
        self.client.logout()
