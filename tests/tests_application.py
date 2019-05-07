from json import loads as jsonloads
from django.test import TestCase, Client
from restapi import models
from . import login

# Create your tests here.
CLIENT = Client()
CLIENT_PLAYER1 = Client()
CLIENT_PLAYER2 = Client()


class RoomTestCase(TestCase):

    def setUpTestData():
        room_owner = models.User.objects.create(username='testuser')
        room_owner.set_password('azerty1234')
        room_owner.save()

        player1 = models.User.objects.create(username='dude')
        player1.set_password('qsdfgh1234')
        player1.save()

        player2 = models.User.objects.create(username='player2')
        player2.set_password('password')
        player2.save()

        pathfinder = models.GameModel(name='pathfinder3.5', dice='d20')
        pathfinder.save()

        room = models.Room(
            name='testroom',
            text_id='randomfox',
            description='testing room stuff',
            max_players=2,
            is_private=False,
            owner=room_owner,
            game_model=pathfinder)
        room.save()

        room_no_apps = models.Room(
            name='testroom_private',
            text_id='peculiarbabbooon',
            description='testing room stuff',
            max_players=2,
            is_private=False,
            owner=room_owner,
            game_model=pathfinder)
        room_no_apps.save()

        application = models.Application(
            text_id='dude-randomfox',
            status='p',
            room_text=room,
            user=player1)
        application.save()

    def setUp(self):
        CLIENT.login(username='testuser', password='azerty1234')
        CLIENT_PLAYER1.login(username='dude', password='qsdfgh1234')
        CLIENT_PLAYER2.login(username='player2', password='password')

    # testing preliminary validation
    def test_application_nonexistent_room(self):
        self.assertEqual(CLIENT.get('/rooms/nonexistent/applications/',
                                    HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 400)

    def test_access_logged_out(self):
        CLIENT.logout()
        self.assertEqual(CLIENT.get('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(CLIENT.post('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(CLIENT.patch('/rooms/randomfox/applications/').status_code, 403)
        self.assertEqual(CLIENT.delete('/rooms/randomfox/applications/').status_code, 403)

    def test_access_not_room_owner(self):
        self.assertEqual(CLIENT_PLAYER1.get('/rooms/randomfox/applications/').status_code, 403)

    # testing the GET method
    def test_no_applications_in_room(self):
        self.assertEqual(CLIENT.get('/rooms/peculiarbabboon/applications/',
                                    HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code, 400)

    def test_applications_list(self):
        self.assertEqual(len(jsonloads(CLIENT.get('/rooms/peculiarbabboon/applications/',
                                                  HTTP_AUTHORIZATION='JWT {}'.format(
                                                      login.login('testuser'))).content)),
                         1)

    # testing the POST method
    def test_application_no_user(self):
        CLIENT_PLAYER2.logout()
        self.assertEqual(CLIENT_PLAYER2.post('/rooms/randomfox/applications/',
                                             {}).status_code,
                         403)

    def test_application_creation(self):
        self.assertEqual(CLIENT_PLAYER2.post('/rooms/randomfox/applications/',
                                              {},
                                              HTTP_AUTHORIZATION='JWT {}'.format(login.login('player2'))).status_code,
                         201)
        self.assertEqual(models.Application.objects.count(), 2)

    # testing the PATCH method
    def test_reply_not_room_owner(self):
        self.assertEqual(CLIENT_PLAYER1.patch('/rooms/randomfox/applications/',
                                      {'text_id': 'dude-randomfox'},
                                      {},
                                      HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         403)

    def test_application_status_nonexistent(self):
        self.assertEqual(CLIENT.patch('/rooms/randomfox/applications/',
                                      {'text_id': 'dude-randomfox'},
                                      {},
                                      HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)

    def test_application_status_invalid(self):
        self.assertEqual(CLIENT.patch('/rooms/randomfox/applications/',
                                      {'text_id': 'dude-randomfox',
                                       'status': 'zzzzz', },
                                      {},
                                      HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)

    def test_application_nonexistent(self):
        self.assertEqual(CLIENT.patch('/rooms/randomfox/applications/',
                                      {'text_id': 'nonexistent',
                                       'status': 'a', },
                                      {},
                                      HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)

    def test_application_edit(self):
        self.assertEqual(CLIENT.patch('/rooms/randomfox/applications/',
                                      {'text_id': 'dude-randomfox',
                                       'status': 'a', },
                                      {},
                                      HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         200)
        self.assertEqual(models.Application.objects.get(text_id__iexact='dude-randomfox').status, 'a')
