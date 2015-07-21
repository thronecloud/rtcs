from django.conf import settings
from django.db import models
from django.utils import timezone

from geoposition.fields import GeopositionField
from model_utils import Choices


class Profile(models.Model):
    GENDER = Choices(
        (1, "FEMALE", "Female"),
        (2, "MALE", "Male")
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    gender = models.IntegerField(choices=GENDER, blank=True, null=True)

    @property
    def email(self):
        return self.user.email

    @property
    def name(self):
        return self.user.first_name

    def __unicode__(self):
        return unicode(self.user)

    @property
    def picture(self):
        sa = self.user.socialaccount_set.filter(provider='facebook').first()
        if sa is not None:
            return '//graph.facebook.com/{0}/picture?type=large'.format(
                sa.extra_data['id'])
        sa = self.user.socialaccount_set.filter(provider='google').first()
        return sa.extra_data.get('picture', '')


# Facebook Specific Models

class Education(models.Model):
    profile = models.ForeignKey(Profile)
    school_id = models.CharField(max_length=255)
    school_name = models.CharField(max_length=255)
    edu_type = models.CharField(max_length=32)

    def __unicode__(self):
        return self.school_id


class Hometown(models.Model):
    profile = models.OneToOneField(Profile)
    hometown_id = models.CharField(max_length=255)
    hometown_name = models.CharField(max_length=255)


class Friend(models.Model):
    profile = models.ForeignKey(Profile)
    friend_id = models.CharField(max_length=255)
    friend_name = models.CharField(max_length=255)


# Request Models

class CabRequest(models.Model):
    GENDER_PREF = Choices(
        (1, "FEMALE", "Female"),
        (2, "MALE", "Male"),
        (999, "ANY", "Any"),
    )
    profile = models.ForeignKey(Profile, related_name='cabrequests')
    origin = GeopositionField()
    destination = GeopositionField()
    moment = models.DateTimeField(default=timezone.now)
    gender = models.IntegerField(
        choices=GENDER_PREF, default=GENDER_PREF.ANY,
        verbose_name="Travel with")
    origin_name = models.CharField(max_length=255, null=True, blank=True)
    destination_name = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.pk)


class DirectionsRoute(models.Model):
    """Store the routes/legs from origin to destination
    of a given CabRequest

    """
    cabrequest = models.ForeignKey(CabRequest, related_name='routes')
    duration = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.pk)


class DirectionsStep(models.Model):
    """Each route/leg contain several steps (see GMaps API)"""

    route = models.ForeignKey(DirectionsRoute, related_name='steps')
    order = models.IntegerField()
    start = GeopositionField()
    end = GeopositionField()

    def __unicode__(self):
        return unicode(self.pk)


class RequestMatch(models.Model):
    request1 = models.ForeignKey(CabRequest, related_name="matches")
    request2 = models.ForeignKey(CabRequest, related_name="references")
    # score = models.FloatField()
    affinity = models.FloatField()
    route_overlap = models.FloatField()
