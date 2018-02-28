from django.test import TestCase, Client
from . import models

# Create your tests here.
c=Client()

class UserTest(TestCase):

    def test_registration(self):
        response=c.post('/register/', {'username': 'testname', 'password1': 'abcdefgh123', 'password2': 'abcdefgh123'})
        self.assertEqual(response.status_code,201)
        user=models.User.objects.get_by_natural_key('testname')