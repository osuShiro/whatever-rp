"""kitsune_odori URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework_jwt.views import refresh_jwt_token
from restapi.views import applications, gamemodels, rooms

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^admin/$', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^', include('rest_auth.urls')),
    url(r'^register/$', include('rest_auth.registration.urls')),
    url(r'^refresh-token/$', refresh_jwt_token),
    url(r'^rooms/(?P<room_text_id>.+)/applications/$',applications.ApplicationEditView.as_view()),
    url(r'^rooms/$', rooms.RoomEditView.as_view()),
    url(r'^gamemodels/$',gamemodels.GamemodelEditView.as_view())
]
