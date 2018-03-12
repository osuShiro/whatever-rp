from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from restapi import models
import json, datetime

# Create your views here.
def rooms(request):
    error = {}
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
    elif request.method=='POST':
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        # check jwt token
        if 'HTTP_AUTHORIZATION' not in request.META.keys():
            error['jwt']='JWT token incorrect or missing.'
        else:
            keys=request.POST.keys()
            # assuming jwt is correct, will do verification later
            # required fields: name, system, max_players
            if 'title' not in keys:
                error['name'] = 'Room name missing.'
            if 'system' not in keys:
                error['system'] = 'Game system missing.'
            if 'max_players' not in keys:
                error['max_players'] = 'Maximum players allowed missing.'
            if not error:
                room_name = request.POST['title']
                try:
                    system = models.GameModel.objects.get(name__iexact=request.POST['system'])
                except ObjectDoesNotExist:
                    error['system'] = 'Game system does not exist.'
                max_players = request.POST['max_players']
                if models.Room.objects.filter(name__iexact=room_name):
                    error['name'] = 'Room name already taken.'
                if not error:
                    description = '' if not request.POST['description'] else request.POST['description']
                    new_room = models.Room(name=room_name,
                        description = description,
                        max_players = max_players,
                        created_at = datetime.datetime.utcnow(),
                        updated_at = datetime.datetime.utcnow(),
                        owner = request.user,
                        system = system)
                    new_room.save()
        if error:
            return HttpResponseBadRequest(json.dumps(error))
        else:
            return HttpResponse(status=201)
    else:
        return HttpResponseBadRequest()