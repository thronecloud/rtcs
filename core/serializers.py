from rest_framework import serializers

from .models import CabRequest
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('gender', 'email', 'name')


class CabRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CabRequest
