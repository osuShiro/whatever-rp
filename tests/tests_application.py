from django.test import TestCase, Client
from restapi import models
from . import login

# Create your tests here.
c = Client()
c_player = Client()

class RoomTestCase(TestCase):

    def setUpTestData():
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

    def setUp(self):
        c.login(username='testuser', password='azerty1234')
        c_player.login(username='dude', password='qsdfgh1234')

    def test_access_logged_out(self):
        # accessing without being logged in should return a Forbidden error code
        c.logout()
        self.assertEqual(c.get('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.post('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.patch('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(c.delete('/rooms/randomfox/applications/').status_code, 403)

    def test_no_applications_in_room(self):
        # accessing a room without applications should return a 400 error code
        self.assertEqual(c.get('/rooms/randomfox/applications/',
            HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 400)

    def test_application_creation(self):
        self.assertEqual(c.post('/rooms/randomfox/applications/',
            {'username': 'dude'},
            HTTP_AUTHORIZATION = 'JWT {}'.format(login.login('testuser'))).status_code, 201)
        self.assertEqual(models.Application.objects.count(), 1)

    def test_access_not_room_owner(self):
        # accessing without being room owner should return a Forbidden error code
        self.assertEqual(c_player.get('/rooms/randomfox/applications/').status_code, 403)

    def test_application_list(self):
        # testing application list now that there is one
        self.assertEqual(c.get('/rooms/randomfox/applications/',
             HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 200)

    def test_application_edit(self):
        # testing application patching
        c_player.post('/rooms/randomfox/applications/',
               {'username': 'dude'},
               HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude')))
        patch_test = c.patch('/rooms/randomfox/applications/',
                {'text_id':'dude-randomfox',
                 'status': 'a'},
                {},
                HTTP_AUTHORIZATION = 'JWT {}'.format(login.login('testuser')))
        self.assertEqual(patch_test.status_code, 200)
        c_player.login(username='dude', password='qsdfgh1234')
        self.assertEqual(c.patch('/rooms/randomfox/applications/',
                                 {'text_id': 'dude-randomfox',
                                  'status': 'a', },
                                 {},
                                 HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         403)
        self.assertEqual(models.Application.objects.get(text_id__iexact='dude-randomfox').status, 'a')