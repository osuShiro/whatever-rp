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
    return_data = {}

    keys = request.POST.keys()
    # required fields: name, game_model, max_players
    if 'title' not in keys:
        return HttpResponseBadRequest(json.dumps({'title': 'Room title missing.'}))
    if 'game_model' not in keys:
        return HttpResponseBadRequest(json.dumps({'game_model': 'Game model title missing.'}))
    if 'max_players' not in keys:
        return HttpResponseBadRequest(json.dumps({'max_players': 'Maximum players allowed missing.'}))

    room_name = request.POST['title']

    # check for game_model existence
    try:
        game_model = models.GameModel.objects.get(name__iexact=request.POST['game_model'])
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({'game_model': 'Game model does not exist.'}))

    max_players = request.POST['max_players']

    # check that room name isn't already taken
    if models.Room.objects.filter(name__iexact=room_name):
        return HttpResponseBadRequest(json.dumps({'name': 'Room name already taken'}))

    # is_private is False by default
    if 'is_private' in keys:
        is_private = request.POST['is_private']
    else:
        is_private = False

    # description is empty by default
    if 'description' in keys:
        description = request.POST['description']
    else:
        description = ''

    # generate text id
    duplicate = True
    text_id = ''
    while duplicate:
        text_id = ANIMALS[randint(0, ANIMALS_COUNT - 1)] + ADJECTIVES[
            randint(0, ADJECTIVE_COUNT - 1)]
        if not list(models.Room.objects.filter(text_id=text_id)):
            duplicate = False

    # create the new room
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

    # return created room's data
    return_data['name'] = room_name
    return_data['text_id'] = new_room.text_id
    return_data['max_players'] = max_players
    return_data['owner'] = request.user.username
    return_data['game_model'] = game_model.name

    return HttpResponse(json.dumps(return_data), status=201)


def rooms_patch(request):
    return_data = {}

    # turn the body of the request (bytes) into usable dictionary
    patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
    keys = patch_data.keys()

    # requirement: room text_id
    if 'text_id' not in keys:
        return HttpResponseBadRequest(json.dumps({'text_id': 'Room name missing'}))

    # checking if room exists
    try:
        room = models.Room.objects.get(text_id=patch_data['text_id'].lower())
        return_data['text_id'] = room.text_id
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({'text_id': 'Room not found.'}))

    # logged in user must be room owner
    if request.user != room.owner:
        return HttpResponseForbidden(json.dumps({'user': 'User is not room owner.'}))

    # update room content based on request data
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
        return HttpResponse(json.dumps({'text_id': 'No text_id found.'}), status=400)

    # check if room exists
    try:
        room = models.Room.objects.get(text_id=request_data['text_id'].lower())
        return_data['text_id'] = room.text_id
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({'text_id': 'Room not found.'}))

    # logged in user must be room owner
    if request.user != room.owner:
        return HttpResponseForbidden(json.dumps({'user': 'User is not room owner.'}))

    room.delete()

    return HttpResponse(status=200)
