from django.test import TestCase, Client
from restapi import models

# Create your tests here.
c = Client()

class RoomTestCase(TestCase):

    def setUp(self):
        new_user=models.User(username='test user',password='azerty1234')
        new_user.save()
        pathfinder=models.GameModel(name='pathfinder3.5', dice='d20')
        pathfinder.save()
        new_room=models.Room(
            name='test room',
            description='testing room stuff',
            owner=new_user,
            system=pathfinder)
        new_room.save()

    def test_room_list(self):
        self.assertEqual(c.put('/rooms/').status_code,400)
        print(c.get('/rooms/').content)
