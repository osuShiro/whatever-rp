from random import randint
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
from stronghold.decorators import public
import json, datetime, os

with open('static/animals.txt','r') as an_file:
    animals = [s.strip() for s in an_file.readlines()]
    animal_number = len(animals)
with open('static/adjectives.txt','r') as adj_file:
    adjectives = [s.strip() for s in adj_file.readlines()]
    adjective_number = len(adjectives)

# Create your views here.
@public
def rooms_get(request):
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
    return HttpResponse(json.dumps(response))

def rooms(request):
    error = {}
    return_data = {}
    if request.method=='GET':
        return rooms_get(request)
    else:
        # all other actions require being logged in
        '''if 'HTTP_AUTHORIZATION' not in request.META.keys():
            pass
            error['jwt']='JWT token incorrect or missing.'
            return HttpResponse(json.dumps(error), status=401)'''
        if request.method=='POST':
            if not request.user.is_authenticated:
                return HttpResponse(status=405)
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
                    if 'is_private' in keys:
                        is_private = request.POST['is_private']
                    else:
                        is_private = False
                    if not error:
                        # generate text id
                        duplicate = True
                        text_id = ''
                        while duplicate:
                            text_id = animals[randint(0, animal_number-1)] + adjectives[randint(0, adjective_number-1)]
                            if list(models.Room.objects.filter(text_id=text_id)) == []:
                                duplicate = False
                        description = '' if not request.POST['description'] else request.POST['description']
                        new_room = models.Room(name=room_name,
                            text_id = text_id.lower(),
                            description = description,
                            max_players = max_players,
                            created_at = datetime.datetime.utcnow(),
                            updated_at = datetime.datetime.utcnow(),
                            is_private = is_private,
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
            keys = patch_data.keys()
            if 'text_id' not in keys:
                error['text_id'] = 'Room name missing.'
            else:
                try:
                    room = models.Room.objects.get(text_id = patch_data['text_id'].lower())
                    return_data['text_id'] = room.text_id
                except ObjectDoesNotExist:
                    return HttpResponseBadRequest('Room not found.')
                if request.user != room.owner:
                    return HttpResponseForbidden()
                for (key, value) in patch_data.items():
                    if key in ('name','description','max_players'):
                        setattr(room,key,value)
                        return_data[key] = value
                room.updated_at = datetime.datetime.utcnow()
                return_data['updated_at'] = room.updated_at.isoformat()
                room.save()
                return HttpResponse(json.dumps(return_data),status=200)
        elif request.method == 'DELETE':
            request_data = json.loads(request.body.decode('utf8').replace("'", '"'))
            if 'text_id' not in request_data.keys():
                error['text_id'] = 'Room name missing.'
            else:
                try:
                    room = models.Room.objects.get(text_id = request_data['text_id'].lower())
                    return_data['text_id'] = room.text_id
                except ObjectDoesNotExist:
                    return HttpResponseBadRequest('Room not found.')
                if request.user != room.owner:
                    return HttpResponseForbidden()
                room.delete()
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)

def gamemodels(request):
    if request.method == 'GET':
        response=[]
        gamemodel_list = list(models.GameModel.objects.all())
        for gamemodel in gamemodel_list:
            dic = {}
            dic['name'] = gamemodel.name
            dic['dice'] = gamemodel.dice
            dic['updated_at'] = gamemodel.updated_at.isoformat()
            response.append(dic)
        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse(status=405)

def applications(request,room_text_id):
    error = {}
    if not room_text_id:
        return HttpResponseBadRequest
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    else:
        # if user is replying to an application
        if request.method == 'PATCH':
            patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
            keys = patch_data.keys()
            if 'text_id' not in keys:
                error['application'] = 'Missing text_id.'
                return HttpResponse(json.dumps(error), status=400)
            elif 'status' not in keys:
                error['status'] = 'No status change to apply.'
                return HttpResponse(json.dumps(error), status=400)
            elif patch_data['status'] not in ('a', 'p', 'r'):
                    error['status'] = 'Invalid status.'
                    return HttpResponse(json.dumps(error), status=400)
            else:
                try:
                    application = models.Application.objects.get(text_id__iexact=patch_data['text_id'])
                except ObjectDoesNotExist:
                    error['application'] = 'Application not found.'
                    return HttpResponse(json.dumps(error), status=400)
                if request.user != application.user:
                    error['user'] = 'This user does not have the right to reply to this application.'
                    return HttpResponse(json.dumps(error), status=403)
                else:
                    application.status = patch_data['status']
                    application.updated_at = datetime.datetime.utcnow()
                    application.save()
                    return HttpResponse(json.dumps({
                        'text_id': application.text_id,
                        'status': application.status,
                        'username': application.user.username,
                        'room': application.room_text.text_id,
                        'updated_at': application.updated_at.isoformat(),
                    }), status=200)
        else:
            try:
                room = models.Room.objects.get(text_id__iexact=room_text_id)
                room_gm = room.owner
            except ObjectDoesNotExist:
                error['room'] = 'Selected room does not exist.'
                return HttpResponse(json.dumps(error), status=400)
            if request.user != room_gm:
                error['user'] = 'Logged in user is not the room\'s owner.'
                return HttpResponse(json.dumps(error), status=403)
            if request.method == 'GET':
                application_list = []
                room_applications = models.Application.objects.filter(room_text=room)
                for app in room_applications:
                    application_list.append({
                        'username': app.user.username,
                        'status': app.status,
                        'text_id': app.text_id,
                        'updated_at': app.updated_at.isoformat(),
                    })
                if application_list:
                    return HttpResponse(json.dumps(application_list), status=200)
                else:
                    error['applications'] = 'No applications found for the room.'
                    return HttpResponse(json.dumps(error), status=400)
            elif request.method == 'POST':
                keys = request.POST.keys()
                if 'username' not in keys:
                    error['user'] = 'Missing applicant User.'
                else:
                    try:
                        user = models.User.objects.get(username__iexact=request.POST['username'])
                    except:
                        error['user'] = 'Not user found for given username.'
                        return HttpResponse(json.dumps(error), status=400)
                if not error:
                    username = request.POST['username']
                    text_id = username + '-' + room_text_id
                    models.Application(text_id=text_id,
                        status='p',
                        updated_at=datetime.datetime.utcnow(),
                        room_text=room,
                        user=user).save()
                    return HttpResponse(status=201)
