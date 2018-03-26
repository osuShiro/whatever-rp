from random import randint
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
import json, datetime, os

with open('static/animals.txt','r') as an_file:
    animals = [s.strip() for s in an_file.readlines()]
    animal_number = len(animals)
with open('static/adjectives.txt','r') as adj_file:
    adjectives = [s.strip() for s in adj_file.readlines()]
    adjective_number = len(adjectives)

# Create your views here.
def rooms(request):
    error = {}
    return_data = {}
    if request.method=='GET':
        response=[]
        room_list=list(models.Room.objects.all())
        for room in room_list:
            room_dic={}
            room_dic['id']=room.id
            room_dic['name']=room.name
            room_dic['description']=room.description
            room_dic['owner']=room.owner.username
            room_dic['updated_at']=room.updated_at.isoformat()
            response.append(room_dic)
        return HttpResponse(json.dumps(response))
    else:
        # all other actions require being logged in
        if 'HTTP_AUTHORIZATION' not in request.META.keys():
            error['jwt']='JWT token incorrect or missing.'
            return HttpResponse(json.dumps(error), status=401)
        if request.method=='POST':
            if not request.user.is_authenticated:
                return HttpResponseForbidden()
            else:
                keys=request.POST.keys()
                # required fields: name, game_model, max_players
                if 'title' not in keys:
                    error['name'] = 'Room name missing.'
                if 'game_model' not in keys:
                    error['game_model'] = 'Game model missing.'
                if 'max_players' not in keys:
                    error['max_players'] = 'Maximum players allowed missing.'
                if not error:
                    room_name = request.POST['title']
                    try:
                        game_model = models.GameModel.objects.get(name__iexact=request.POST['game_model'])
                    except ObjectDoesNotExist:
                        error['game_model'] = 'Game model does not exist.'
                    max_players = request.POST['max_players']
                    if models.Room.objects.filter(name__iexact=room_name):
                        error['name'] = 'Room name already taken.'
                    if not error:
                        # generate text id
                        duplicate = False
                        animal = ''
                        adjective = ''
                        while duplicate:
                            animal = animals[randint(animal_number)]
                            adjective = adjectives[randint(adjective_number)]
                            if models.Room.objects.filter(text_id=adjective+animal) != []:
                                duplicate = True
                            else:
                                duplicate = False
                        description = '' if not request.POST['description'] else request.POST['description']
                        new_room = models.Room(name=room_name,
                            text_id = (adjective+animal).lower(),
                            description = description,
                            max_players = max_players,
                            created_at = datetime.datetime.utcnow(),
                            updated_at = datetime.datetime.utcnow(),
                            owner = request.user,
                            game_model = game_model)
                        new_room.save()
                        return_data['name'] = room_name
                        return_data['text_id'] = new_room.text_id
                        return_data['max_players'] = max_players
                        return_data['owner'] = request.user.username
                        return_data['game_model'] = game_model.name
            if error:
                return HttpResponseBadRequest(json.dumps(error))
            else:
                return HttpResponse(json.dumps(return_data), status=201)
        elif request.method == 'PATCH':
            # requirement: room text_id
            # turn the body of the request (bytes) into usable dictionary
            patch_data = json.loads(request.body.decode('utf8').replace("'",'"'))
            print(patch_data)
            keys = patch_data.keys()
            if 'text_id' not in keys:
                error['text_id'] = 'Room name missing.'
            else:
                try:
                    room = models.Room.objects.get(text_id = patch_data['text_id'].lower())
                    return_data['text_id'] = room.text_id
                except ObjectDoesNotExist:
                    return HttpResponseBadRequest('Room not found.')
                for (key, value) in patch_data.items():
                    if key in ('name','description','max_players'):
                        setattr(room,key,value)
                        return_data[key] = value
                room.updated_at = datetime.datetime.utcnow()
                return_data['updated_at'] = room.updated_at.isoformat()
                room.save()
                return HttpResponse(json.dumps(return_data),status=200)
        else:
            return HttpResponse(status=405)