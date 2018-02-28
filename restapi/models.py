import datetime
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class GameModel(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    dice = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(default=datetime.datetime.utcnow(), editable=False)
    updated_at = models.DateTimeField(default=datetime.datetime.utcnow())