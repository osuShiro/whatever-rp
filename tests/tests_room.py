from django.test import TestCase, Client
from restapi import models
from . import login

# Create your tests here.
c = Client()

class RoomTestCase(TestCase):

    def setUp(self):
        new_user = models.User.objects.create(username='testuser')
        new_user.set_password('azerty1234')
        new_user.save()
        pathfinder=models.GameModel(name='pathfinder3.5', dice='d20')
        pathfinder.save()
        new_room=models.Room(
            name='testroom',
            description='testing room stuff',
            max_players=2,
            owner=new_user,
            system=pathfinder)
        new_room.save()

    def test_room_list(self):
        self.assertEqual(c.put('/rooms/').status_code,400)
        print(c.get('/rooms/').content)
        c.login(username='testuser', password='azerty1234')
        self.assertEqual(c.post('/rooms/',
            {},
            HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
            400)
        self.assertEqual(c.post('/rooms/',
            {'title':'testtitle',
                'description':'test description',
                'system':'pathfinder3.5',
                'max_players': 8},
            HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
            201)
        self.assertEqual(models.Room.objects.count(),2)