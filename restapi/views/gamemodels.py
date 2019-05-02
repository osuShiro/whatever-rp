from restapi import models
import json, datetime
from stronghold.decorators import public
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

@public
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