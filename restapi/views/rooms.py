from random import randint
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
import json, datetime
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from stronghold.decorators import public

with open('static/animals.txt','r') as an_file:
    animals = [s.strip() for s in an_file.readlines()]
    animal_number = len(animals)
with open('static/adjectives.txt','r') as adj_file:
    adjectives = [s.strip() for s in adj_file.readlines()]
    adjective_number = len(adjectives)

class RoomEditView(GenericAPIView):
    error = {}
    return_data = {}

    @public
    def get(self, request):
        response = []
        room_list = list(models.Room.objects.all())
        for room in room_list:
            if room.is_private:
                continue
            room_dic = {}
            room_dic['text_id'] = room.text_id
            room_dic['name'] = room.name
            room_dic['description'] = room.description
            room_dic['owner'] = room.owner.username
            room_dic['game_model'] = room.game_model.name
            room_dic['updated_at'] = room.updated_at.isoformat()
            response.append(room_dic)
        return Response(json.dumps(response))

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=405)
        else:
            keys = request.POST.keys()
            # required fields: name, game_model, max_players
            if 'title' not in keys:
                self.error['name'] = 'Room name missing.'
            if 'game_model' not in keys:
                self.error['game_model'] = 'Game model missing.'
            if 'max_players' not in keys:
                self.error['max_players'] = 'Maximum players allowed missing.'
            if not self.error:
                room_name = request.POST['title']
                try:
                    game_model = models.GameModel.objects.get(name__iexact=request.POST['game_model'])
                except ObjectDoesNotExist:
                    self.error['game_model'] = 'Game model does not exist.'
                max_players = request.POST['max_players']
                if models.Room.objects.filter(name__iexact=room_name):
                    self.error['name'] = 'Room name already taken.'
                if 'is_private' in keys:
                    is_private = request.POST['is_private']
                else:
                    is_private = False
                if not self.error:
                    # generate text id
                    duplicate = True
                    text_id = ''
                    while duplicate:
                        text_id = animals[randint(0, animal_number - 1)] + adjectives[randint(0, adjective_number - 1)]
                        if list(models.Room.objects.filter(text_id=text_id)) == []:
                            duplicate = False
                    description = '' if not request.POST['description'] else request.POST['description']
                    new_room = models.Room(name=room_name,
                                           text_id=text_id.lower(),
                                           description=description,
                                           max_players=max_players,
                                           created_at=datetime.datetime.utcnow(),
                                           updated_at=datetime.datetime.utcnow(),
                                           is_private=is_private,
                                           owner=request.user,
                                           game_model=game_model)
                    new_room.save()
                    self.return_data['name'] = room_name
                    self.return_data['text_id'] = new_room.text_id
                    self.return_data['max_players'] = max_players
                    self.return_data['owner'] = request.user.username
                    self.return_data['game_model'] = game_model.name
            if self.error:
                return Response(exception=True, data=json.dumps(self.error), status=400)
            else:
                return Response(data=json.dumps(self.return_data), status=201)

    def patch(self, request):
        # requirement: room text_id
        # turn the body of the request (bytes) into usable dictionary
        patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
        keys = patch_data.keys()
        if 'text_id' not in keys:
            self.error['text_id'] = 'Room name missing.'
        else:
            try:
                room = models.Room.objects.get(text_id=patch_data['text_id'].lower())
                self.return_data['text_id'] = room.text_id
            except ObjectDoesNotExist:
                return Response('Room not found.', exception=True, status=400)
            if request.user != room.owner:
                return Response(status=403)
            for (key, value) in patch_data.items():
                if key in ('name', 'description', 'max_players'):
                    setattr(room, key, value)
                    self.return_data[key] = value
            room.updated_at = datetime.datetime.utcnow()
            self.return_data['updated_at'] = room.updated_at.isoformat()
            room.save()
            return Response(data=json.dumps(self.return_data), status=200)

    def delete(self, request):
        request_data = json.loads(request.body.decode('utf8').replace("'", '"'))
        if 'text_id' not in request_data.keys():
            self.error['text_id'] = 'Room name missing.'
        else:
            try:
                room = models.Room.objects.get(text_id=request_data['text_id'].lower())
                self.return_data['text_id'] = room.text_id
            except ObjectDoesNotExist:
                return Response('Room not found.', exception=True, status=400)
            if request.user != room.owner:
                return Response(status=403)
            room.delete()
            return Response(status=200)