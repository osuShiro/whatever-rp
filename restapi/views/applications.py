from random import randint
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
import json, datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from stronghold.decorators import public

def applications(request, room_text_id=None):
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