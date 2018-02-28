from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from restapi import models as rp_models
import json

# Create your views here.
def rooms(request):
    if request.method=='GET':
        response=[]
        room_list=list(rp_models.Room.objects.filter())
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
        return HttpResponseBadRequest()