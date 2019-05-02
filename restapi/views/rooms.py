import datetime, json
from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from stronghold.decorators import public
from restapi import models

with open('static/animals.txt', 'r') as an_file:
    ANIMALS = [s.strip() for s in an_file.readlines()]
    ANIMALS_COUNT = len(ANIMALS)
with open('static/adjectives.txt', 'r') as adj_file:
    ADJECTIVES = [s.strip() for s in adj_file.readlines()]
    ADJECTIVE_COUNT = len(ADJECTIVES)


@public
def rooms(request):
    if request.method == 'GET':
        return rooms_get()

    # all other methods require being authenticated

    if not request.user.is_authenticated:
        return HttpResponse(status=405)

    if request.method == 'POST':
        return rooms_post(request)
    if request.method == 'PATCH':
        return rooms_patch(request)
    if request.method == 'DELETE':
        return rooms_delete(request)
    return HttpResponse(status=405)


def rooms_get():
    response = []
    room_list = list(models.Room.objects.all())

    for room in room_list:
        if not room.is_private:
            room_dic = {'text_id': room.text_id,
                        'name': room.name,
                        'description': room.description,
                        'owner': room.owner.username,
                        'game_model': room.game_model.name,
                        'updated_at': room.updated_at.isoformat()
                        }
            response.append(room_dic)

    return HttpResponse(json.dumps(response))


def rooms_post(request):
    error = {}
    return_data = {}

    keys = request.POST.keys()
    # required fields: name, game_model, max_players
    if 'title' not in keys:
        error['name'] = 'Room name missing.'
    if 'game_model' not in keys:
        error['game_model'] = 'Game model missing.'
    if 'max_players' not in keys:
        error['max_players'] = 'Maximum players allowed missing.'
    if error:
        return HttpResponseBadRequest(json.dumps(error))
    room_name = request.POST['title']

    try:
        game_model = models.GameModel.objects.get(name__iexact=request.POST['game_model'])
    except ObjectDoesNotExist:
        error['game_model'] = 'Game model does not exist.'

    max_players = request.POST['max_players']

    if models.Room.objects.filter(name__iexact=room_name):
        return HttpResponseBadRequest(json.dumps({'name':'Room name already taken'}))

    if 'is_private' in keys:
        is_private = request.POST['is_private']
    else:
        is_private = False

    # generate text id
    duplicate = True
    text_id = ''
    while duplicate:
        text_id = ANIMALS[randint(0, ANIMALS_COUNT - 1)] + ADJECTIVES[
            randint(0, ADJECTIVE_COUNT - 1)]
        if not list(models.Room.objects.filter(text_id=text_id)):
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
    return_data['name'] = room_name
    return_data['text_id'] = new_room.text_id
    return_data['max_players'] = max_players
    return_data['owner'] = request.user.username
    return_data['game_model'] = game_model.name

    return HttpResponse(json.dumps(return_data), status=201)


def rooms_patch(request):
    return_data = {}

    # requirement: room text_id
    # turn the body of the request (bytes) into usable dictionary
    patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
    keys = patch_data.keys()

    if 'text_id' not in keys:
        return HttpResponseBadRequest(json.dumps({'text_id': 'Room name missing'}))

    try:
        room = models.Room.objects.get(text_id=patch_data['text_id'].lower())
        return_data['text_id'] = room.text_id
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Room not found.')

    if request.user != room.owner:
        return HttpResponseForbidden()

    for (key, value) in patch_data.items():
        if key in ('name', 'description', 'max_players'):
            setattr(room, key, value)
            return_data[key] = value

    room.updated_at = datetime.datetime.utcnow()
    return_data['updated_at'] = room.updated_at.isoformat()
    room.save()

    return HttpResponse(json.dumps(return_data), status=200)


def rooms_delete(request):
    return_data = {}
    request_data = json.loads(request.body.decode('utf8').replace("'", '"'))

    if 'text_id' not in request_data.keys():
        return HttpResponse('Room not found', status=400)

    try:
        room = models.Room.objects.get(text_id=request_data['text_id'].lower())
        return_data['text_id'] = room.text_id
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Room not found.')

    if request.user != room.owner:
        return HttpResponseForbidden()

    room.delete()
    
    return HttpResponse(status=200)
