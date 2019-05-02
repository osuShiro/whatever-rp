from restapi import models
import json, datetime
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class GamemodelEditView(GenericAPIView):
    def get(self):
        response = []
        gamemodel_list = list(models.GameModel.objects.all())
        for gamemodel in gamemodel_list:
            dic = {}
            dic['name'] = gamemodel.name
            dic['dice'] = gamemodel.dice
            dic['updated_at'] = gamemodel.updated_at.isoformat()
            response.append(dic)
        return Response(data=json.dumps(response), status=200)