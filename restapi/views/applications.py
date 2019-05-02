from random import randint
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
import json, datetime
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class ApplicationEditView(GenericAPIView):
    error = {}

    def get_room(self, request, room_text_id):
        try:
            room = models.Room.objects.get(text_id__iexact=room_text_id)
            room_gm = room.owner
        except ObjectDoesNotExist:
            return Response('Selected room does not exist.', status=404)
        if request.user != room_gm:
            return Response('Logged in user is not the room\'s owner.', status=403)
        return room

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response(status=403)
        else:
            patch_data = json.loads(request.body.decode('utf8').replace("'", '"'))
            keys = patch_data.keys()
            if 'text_id' not in keys:
                return Response('Missing text_id', status=400)
            elif 'status' not in keys:
                return Response('No status change to apply.', status=400)
            elif patch_data['status'] not in ('a', 'p', 'r'):
                return Response('Invalid application status.', status=400)
            else:
                try:
                    application = models.Application.objects.get(text_id__iexact=patch_data['text_id'])
                except ObjectDoesNotExist:
                    return Response('Application not found', status=400)
                if request.user != application.user:
                    return Response('This user does not have the right to reply to this application.', status=403)
                else:
                    application.status = patch_data['status']
                    application.updated_at = datetime.datetime.utcnow()
                    application.save()
                    return Response(json.dumps({
                        'text_id': application.text_id,
                        'status': application.status,
                        'username': application.user.username,
                        'room': application.room_text.text_id,
                        'updated_at': application.updated_at.isoformat(),
                    }), status=200)

    def get(self, request, room_text_id=None):
        room = self.get_room(request, room_text_id)
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
            return Response(data=json.dumps(application_list), status=200)
        else:
            return Response('No applications found for the room.', status=400)

    def post(self, request, room_text_id=None):
        room = self.get_room(request, room_text_id)
        keys = request.POST.keys()
        if 'username' not in keys:
            self.error['user'] = 'Missing applicant User.'
        else:
            try:
                user = models.User.objects.get(username__iexact=request.POST['username'])
            except:
                self.error['user'] = 'Not user found for given username.'
                return Response(data=json.dumps(self.error), status=400)
        if not self.error:
            username = request.POST['username']
            text_id = username + '-' + room_text_id
            models.Application(text_id=text_id,
                               status='p',
                               updated_at=datetime.datetime.utcnow(),
                               room_text=room,
                               user=user).save()
            return Response(status=201)

    def put(self):
        return Response(status=405)