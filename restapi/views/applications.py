import datetime, json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from restapi import models


def applications(request, room_text_id=None):
    # check for text_id existence
    if not room_text_id:
        return HttpResponseBadRequest(json.dumps({'text_id':'text_id missing.'}))

    # check if room exists
    try:
        room = models.Room.objects.get(text_id__iexact=room_text_id)
        room_gm = room.owner
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'room': 'Selected room does not exist.'}), status=400)

    # applications are not available to logged out users
    if not request.user.is_authenticated:
        return HttpResponseForbidden(json.dumps({'user': 'No user logged in.'}))

    # room owner checking applications to their room
    if request.method == 'GET':
        return application_get(request, room, room_gm)

    # applying to a room
    elif request.method == 'POST':
        return application_post(request, room)

    # if user is replying to an application
    if request.method == 'PATCH':
        return application_reply(request, room_gm)

    return HttpResponse(status=405)


def application_get(request, room, room_gm):
    application_list = []
    room_applications = models.Application.objects.filter(room_text=room)

    # applications are not available to anyone but the room owner
    if request.user != room_gm:
        return HttpResponseForbidden(json.dumps({'user': 'Logged in user is not the room\'s owner.'}))

    for app in room_applications:
        application_list.append({
            'username': app.user.username,
            'status': app.status,
            'text_id': app.text_id,
            'updated_at': app.updated_at.isoformat(),
        })

    if application_list:
        return HttpResponse(json.dumps(application_list), status=200)

    return HttpResponse(json.dumps({'applications':'No applications found for this room.'}), status=400)


def application_post(request, room):
    return_data = {}

    username = request.user.username

    # testing if user exists
    try:
        user = models.User.objects.get(username__iexact=username)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({'user': 'No user found for given username'}))

    # create application
    text_id = username + '-' + room.text_id

    models.Application(text_id=text_id,
                       status='p',
                       updated_at=datetime.datetime.utcnow(),
                       room_text=room,
                       user=user).save()

    return_data['text_id'] = text_id
    return_data['status'] = 'p'
    return_data['room_text'] = room.name
    return_data['user'] = user.username

    return HttpResponse(json.dumps(return_data), status=201)


def application_reply(request, room_gm):

    patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
    keys = patch_data.keys()

    # applications are not available to anyone but the room owner
    if request.user != room_gm:
        return HttpResponseForbidden(json.dumps({'user': 'Logged in user is not the room\'s owner.'}))

    # status is the only thing that can be changed
    if 'status' not in keys:
        return HttpResponse(json.dumps({'status': 'No status change to apply.'}), status=400)

    if patch_data['status'] not in ('a', 'p', 'r'):
        return HttpResponse(json.dumps({'status': 'Invalid status'}), status=400)

    # testing if application exists
    try:
        application = models.Application.objects.get(text_id__iexact=patch_data['text_id'])
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'application': 'Application not found'}), status=400)

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
