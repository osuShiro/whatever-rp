import datetime, json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from restapi import models


def applications(request, room_text_id=None):
    error = {}

    if not room_text_id:
        return HttpResponseBadRequest

    if not request.user.is_authenticated:
        return HttpResponse(status=403)

    try:
        room = models.Room.objects.get(text_id__iexact=room_text_id)
        room_gm = room.owner
    except ObjectDoesNotExist:
        error['room'] = 'Selected room does not exist.'
        return HttpResponse(json.dumps(error), status=400)

    if request.user != room_gm:
        error['user'] = 'Logged in user is not the room\'s owner.'
        return HttpResponseForbidden(json.dumps(error))

    # room owner checking applications to their room
    if request.method == 'GET':
        application_get(room)

    # if user is replying to an application
    if request.method == 'PATCH':
        application_reply(request)

    # applying to a room
    elif request.method == 'POST':
        return application_post(request, room_text_id, room)

    return HttpResponse(status=405)


def application_reply(request):

    patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
    keys = patch_data.keys()

    if 'text_id' not in keys:
        return HttpResponse(json.dumps({'application': 'Missing text_id'}), status=400)

    if 'status' not in keys:
        return HttpResponse(json.dumps({'status': 'No status change to apply.'}), status=400)

    if patch_data['status'] not in ('a', 'p', 'r'):
        return HttpResponse(json.dumps({'status': 'Invalid status'}), status=400)

    try:
        application = models.Application.objects.get(text_id__iexact=patch_data['text_id'])
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'application':'Application not found'}), status=400)

    if request.user != application.user:
        return HttpResponse(json.dumps({'user':'This user does not have the right to reply to this application'}),
                            status=403)

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


def application_get(room):
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

    return HttpResponse(json.dumps({'applications':'No applications found for this room.'}), status=400)


def application_post(request, room_text_id, room):
    keys = request.POST.keys()
    if 'username' not in keys:
        return HttpResponseBadRequest(json.dumps({'user': 'Missing applicant User'}))

    try:
        user = models.User.objects.get(username__iexact=request.POST['username'])
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'user': 'No user found for given username'}), status=400)

    text_id = request.POST['username'] + '-' + room_text_id

    models.Application(text_id=text_id,
                       status='p',
                       updated_at=datetime.datetime.utcnow(),
                       room_text=room,
                       user=user).save()

    return HttpResponse(status=201)
