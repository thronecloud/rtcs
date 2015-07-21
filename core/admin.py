from django.contrib import admin

from .models import CabRequest
from .models import DirectionsStep
from .models import DirectionsRoute
from .models import Education
from .models import Friend
from .models import Hometown
from .models import Profile
from .models import RequestMatch


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'school_id', 'school_name', 'edu_type')


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile', 'friend_id', 'friend_name')


@admin.register(Hometown)
class HometownAdmin(admin.ModelAdmin):
    list_display = ('profile', 'hometown_id', 'hometown_name')


@admin.register(CabRequest)
class CabRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'gender', 'moment')


@admin.register(RequestMatch)
class RequestMatchAdmin(admin.ModelAdmin):
    list_display = ('request1', 'request2', 'route_overlap', 'affinity')


@admin.register(DirectionsRoute)
class DirectionsRouteAdmin(admin.ModelAdmin):
    list_display = ('cabrequest', 'duration')


@admin.register(DirectionsStep)
class DirectionsStepAdmin(admin.ModelAdmin):
    list_display = ('route', 'order', 'start', 'end')
    ordering = ('route', 'order')
