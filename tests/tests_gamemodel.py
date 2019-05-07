from json import loads as jsonloads
from django.test import TestCase, Client
from restapi import models

CLIENT = Client()


class GameModelTestCase(TestCase):

    def setUpTestData():
        pathfinder = models.GameModel(name='pathfinder3.5',
                                      dice='d20')
        pathfinder.save()

    def test_gamemodel_list(self):
        self.assertEqual(len(jsonloads(CLIENT.get('/gamemodels/').content)), 1)

    def test_gamemodel_not_get(self):
        self.assertEqual(CLIENT.post('/gamemodels/').status_code, 405)
        self.assertEqual(CLIENT.patch('/gamemodels/').status_code, 405)
        self.assertEqual(CLIENT.delete('/gamemodels/').status_code, 405)
