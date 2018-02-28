from django.test import TestCase, Client
from restapi import models

# Create your tests here.
c = Client()

class UserTestCase(TestCase):

    def test_registration(self):
        user_count=models.User.objects.count()
        response=c.post('/register/', {'username':'testname','password1':'abcdefgh1234','password2':'abcdefgh1234'})
        self.assertEqual(response.status_code,201)
        self.assertEqual(models.User.objects.count(),user_count+1)