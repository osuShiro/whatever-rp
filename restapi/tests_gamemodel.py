from django.test import TestCase, Client
from . import models

# Create your tests here.
c = Client()

class RoomTestCase(TestCase):

    def setUp(self):
        pathfinder=models.GameModel(name='pathfinder3.5',dice='d20')
        pathfinder.save()

    def test_game_model(self):
        self.assertEqual(models.GameModel.objects.count(),1)
        pathfinder=models.GameModel.objects.get(name='pathfinder3.5')
        self.assertEqual(pathfinder.name,'pathfinder3.5')
        self.assertEqual(pathfinder.dice,'d20')
        print(pathfinder.created_at)
        print(pathfinder.updated_at)