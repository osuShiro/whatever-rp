import datetime
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User

APPLICATION_STATUS = (
    ('p','pending'),
    ('a','accepted'),
    ('r','rejected'),
)

# Create your models here.
class GameModel(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    dice = models.CharField(max_length=32, null=False, blank=False)
    created_at = models.DateTimeField(default=datetime.datetime.utcnow(), editable=False)
    updated_at = models.DateTimeField(default=datetime.datetime.utcnow())

    def __str__(self):
        return self.name + '(' + self.dice + ')'

class Room(models.Model):
    name = models.CharField(max_length=256)
    text_id = models.CharField(max_length=128, default='', unique=True)
    description = models.TextField(null=True, blank=True)
    max_players = models.IntegerField(default=8)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.utcnow(), editable=False)
    updated_at = models.DateTimeField(default=datetime.datetime.utcnow())

    owner = models.ForeignKey(User)
    game_model = models.ForeignKey(GameModel)

class Application(models.Model):
    text_id = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=1, choices=APPLICATION_STATUS, default='p')
    created_at = models.DateTimeField(default=datetime.datetime.utcnow(), editable=False)
    updated_at = models.DateTimeField(default=datetime.datetime.utcnow())

    room_text = models.ForeignKey(Room)
    user = models.ForeignKey(User)