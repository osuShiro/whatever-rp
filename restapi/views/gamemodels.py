import json
from stronghold.decorators import public
from django.http import HttpResponse
from restapi import models


@public
def gamemodels(request):
    if request.method == 'GET':
        response = []
        gamemodel_list = list(models.GameModel.objects.all())

        for gamemodel in gamemodel_list:
            dic = {'name': gamemodel.name,
                   'dice': gamemodel.dice,
                   'updated_at': gamemodel.updated_at.isoformat()
                   }
            response.append(dic)
        return HttpResponse(json.dumps(response))

    return HttpResponse(status=405)
