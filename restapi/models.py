import datetime
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
for app in apps.get_app_configs():
    for model in app.get_models():
        pass