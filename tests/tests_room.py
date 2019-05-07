from django.test import TestCase, Client
from restapi import models
from . import login
from json import loads as jsonloads

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
            is_private=True,
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

    def test_room_list(self):
        # there should only be one room in the list (one is private)
        self.assertEqual(len(jsonloads(CLIENT.get('/rooms/').content)),1)

    def test_create_room_no_data(self):
        # missing title, game_model, max_players should lead to a 400 bad request
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'description': 'test description',
                                      'game_model': 'pathfinder3.5',
                                      'max_players': 8},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'max_players': 8},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'game_model': 'pathfinder3.5'},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)
        # missing description should still work
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'game_model': 'pathfinder3.5',
                                      'max_players': 8},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         201)

    def test_create_room_wrong_gamemodel(self):
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'game_model': 'notexist',
                                      'max_players': 8},
                                     HTTP_AUTHORIZATION='JWT {}'.format(login.login('testuser'))).status_code,
                         400)

    def create_room_duplicate_name(self):
        self.assertEqual(CLIENT.post('/rooms/',
                                     {'title': 'testtitle',
                                      'description': 'test description',
                                      'game_model': 'pathfinder3.5',
                                      'max_players': 8},
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
        # checking that the room's unique name has been generated
        self.assertNotEqual(models.Room.objects.get(name='testtitle').text_id, '')

    def test_edit_room_no_textid(self):
        self.assertEqual(CLIENT.patch('/rooms/',
                                             {'name': 'edited name',
                                              'description': 'edited description',
                                              'max_players': 8},
                                             {},
                                             HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         400)

    def test_edit_nonexistent_room(self):
        self.assertEqual(CLIENT.patch('/rooms/',
                                      {'title':'blabla'}).status_code,
                         400)

    def test_edit_room_not_owner(self):
        self.assertEqual(CLIENT_PLAYER.patch('/rooms/',
                                             {'text_id': 'randomfox',
                                              'name': 'edited name',
                                              'description': 'edited description',
                                              'max_players': 8},
                                             {},
                                             HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         403)

    def test_delete_room_no_textid(self):
        self.assertEqual(CLIENT.delete('/rooms/',
                                       {}).status_code,
                         400)

    def test_delete_nonexistent_room(self):
        self.assertEqual(CLIENT.delete('/rooms/',
                                      {'title': 'blabla'}).status_code,
                         400)

    def test_delete_room_not_owner(self):
        self.assertEqual(CLIENT_PLAYER.delete('/rooms/',
                                       {'text_id': 'randomfox'}).status_code,
                         403)

    def test_delete_room(self):
        self.assertEqual(CLIENT.delete('/rooms/',
                                       {'text_id': 'randomfox', },
                                       {},
                                       HTTP_AUTHORIZATION='JWT {}'.format(login.login('dude'))).status_code,
                         200)
        self.assertEqual(models.Room.objects.count(), 1)
