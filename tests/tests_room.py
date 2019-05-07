from django.test import TestCase, Client
from restapi import models
from . import login

# Create your tests here.
CLIENT = Client()
CLIENT_PLAYER = Client()


class RoomTestCase(TestCase):

    def setUpTestData():
        room_owner = models.User.objects.create(username='testuser')
        room_owner.set_password('azerty1234')
        room_owner.save()

        player1 = models.User.objects.create(username='dude')
        player1.set_password('qsdfgh1234')
        player1.save()

        pathfinder = models.GameModel(name='pathfinder3.5', dice='d20')
        pathfinder.save()

        room_public = models.Room(
            name='testroom',
            text_id='randomfox',
            description='testing room stuff',
            max_players=2,
            is_private=False,
            owner=room_owner,
            game_model=pathfinder)
        room_public.save()

        room_private = models.Room(
            name='testroom_private',
            text_id='peculiarbabbooon',
            description='testing room stuff',
            max_players=2,
            is_private=False,
            owner=room_owner,
            game_model=pathfinder)
        room_private.save()

    def setUp(self):
        CLIENT.login(username='testuser', password='azerty1234')
        CLIENT_PLAYER.login(username='dude', password='qsdfgh1234')

    def test_logged_out(self):
        # before logging in
        CLIENT.logout()
        self.assertEqual(CLIENT.get('/rooms/').status_code, 200)
        self.assertEqual(CLIENT.put('/rooms/').status_code, 405)
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'game_model': 'pathfinder3.5',
                                      'max_players': 8}).status_code,
                         405)

    def test_create_room_no_data(self):
        self.assertEqual(CLIENT.post('/rooms/',
                                     {},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)

    def test_create_room(self):
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'game_model': 'pathfinder3.5',
                                      'max_players': 8},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         201)
        self.assertEqual(models.Room.objects.count(), 3)
        self.assertNotEqual(models.Room.objects.get(name='testtitle').text_id, '')

    def test_edit_room_not_owner(self):
        self.assertEqual(CLIENT_PLAYER.patch('/rooms/',
                                             {'text_id': 'randomfox',
                                              'name': 'edited name',
                                              'description': 'edited description',
                                              'max_players': 8},
                                             {},
                                             HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         403)

    def test_delete_room(self):
        self.assertEqual(CLIENT.delete('/rooms/',
                                       {'text_id': 'randomfox', },
                                       {},
                                       HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         200)
        self.assertEqual(models.Room.objects.count(), 1)
