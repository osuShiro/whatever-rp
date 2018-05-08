from django.test import TestCase, Client
from restapi import models
from . import login

# Create your tests here.
c = Client()
c_player = Client()

class RoomTestCase(TestCase):

    def setUp(self):
        new_user = models.User.objects.create(username='testuser')
        new_user.set_password('azerty1234')
        new_user.save()
        second_user = models.User.objects.create(username='dude')
        second_user.set_password('qsdfgh1234')
        second_user.save()
        pathfinder = models.GameModel(name='pathfinder3.5', dice='d20')
        pathfinder.save()
        new_room = models.Room(
            name = 'testroom',
            text_id = 'randomfox',
            description = 'testing room stuff',
            max_players = 2,
            is_private = False,
            owner = new_user,
            game_model = pathfinder)
        new_room.save()

    def test_applications(self):
        # accessing without being logged in should return a Forbidden error code
        self.assertEqual(c.get('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.post('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.patch('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.delete('/rooms/randomfox/applications/').status_code, 403)
        # accessing without being room owner should return a Forbidden error code
        c_player.login(username='dude', password='qsdfgh1234')
        self.assertEqual(c.get('/rooms/randomfox/applications/').status_code, 403)
        # accessing a room without applications should return a 400 error code
        c.login(username='testuser', password='azerty1234')
        self.assertEqual(c.get('/rooms/randomfox/applications/',
            HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 400)
        # testing application creation
        self.assertEqual(c.post('/rooms/randomfox/applications/',
            {'username': 'dude'},
            HTTP_AUTHORIZATION = 'JWT {}'.format(login.login('testuser'))).status_code, 201)
        self.assertEqual(models.Application.objects.count(), 1)
        # testing application list now that there is one
        self.assertEqual(c.get('/rooms/randomfox/applications/',
             HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 200)
        # testing application patching
        self.assertEqual(c.patch('/rooms/randomfox/applications/',
                {'text_id':'dude-randomfox',
                 'status': 'a',},
                {},
                HTTP_AUTHORIZATION = 'JWT {}'.format(login.login('testuser'))).status_code,
                403)
        self.assertEqual(c_player.patch('/rooms/randomfox/applications/',
                                 {'text_id': 'dude-randomfox',
                                  'status': 'a', },
                                 {},
                                 HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         200)
        self.assertEqual(models.Application.objects.get(text_id__iexact='dude-randomfox').status, 'a')