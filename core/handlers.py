import datetime
import googlemaps
import logging
import math

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy.distance import great_circle
from geoposition import Geoposition

from .models import CabRequest
from .models import DirectionsStep
from .models import DirectionsRoute
from .models import Education
from .models import Friend
from .models import Hometown
from .models import Profile
from .models import RequestMatch


logger = logging.getLogger("cabshare")


def gf(geopoint):
    return (float(geopoint.latitude), float(geopoint.longitude))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=CabRequest)
def get_directions(sender, instance, created, **kwargs):
    if created:
        cr = instance
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # Fetch names for the points (origin, destination)
        addr = gmaps.reverse_geocode(gf(cr.origin))
        if addr:
            cr.origin_name = addr[0]['formatted_address']
        addr = gmaps.reverse_geocode(gf(cr.destination))
        if addr:
            cr.destination_name = addr[0]['formatted_address']
        if cr.origin_name or cr.destination_name:
            cr.save()

        directions = gmaps.directions(
            gf(cr.origin),
            gf(cr.destination),
            mode="driving",
            alternatives=True)
        for route in directions:
            leg = route['legs'][0]
            r = DirectionsRoute(
                cabrequest=cr,
                duration=leg['duration']['value'])
            r.save()
            for order, step in enumerate(leg['steps']):
                start = Geoposition(
                    step['start_location']['lat'],
                    step['start_location']['lng'])
                end = Geoposition(
                    step['end_location']['lat'],
                    step['end_location']['lng'])
                s = DirectionsStep(
                    route=r, start=start, end=end, order=order + 1)
                s.save()

        make_pool(cr)


@receiver(post_save, sender=SocialAccount)
def update_profile(sender, instance, created, **kwargs):
        if created and instance.provider == 'facebook':
            logger.info("Updating profile for {}".format(instance.user.email))
            p = instance.user.profile
            dat = instance.extra_data
            gender = dat.get('gender', None)
            if gender == 'male':
                p.gender = p.GENDER.MALE
                p.save()
            elif gender == 'female':
                p.gender = p.GENDER.FEMALE
                p.save()

            for edu in dat.get('education', []):
                item = Education(
                    profile=p,
                    school_id=edu['school']['id'],
                    school_name=edu['school']['name'],
                    edu_type=edu['type'])
                item.save()

            if 'friends' in dat:
                for friend in dat['friends'].get('data', []):
                    item = Friend(
                        profile=p,
                        friend_id=friend['id'],
                        friend_name=friend['name'])
                    item.save()

            if 'hometown' in dat:
                ht = dat['hometown']
                item = Hometown(
                    profile=p,
                    hometown_id=ht['id'],
                    hometown_name=ht['name'])
                item.save()


def calculate_distance(req, routes, distance_going):
    sourcem = gf(req.origin)
    destm = gf(req.destination)
    values = []
    for destr, mvp in enumerate(routes):
        ck = 0
        lmvp = len(mvp) - 1
        for destuin, smvp in enumerate(mvp):
            if ck == 0:
                dists = great_circle(smvp, sourcem).meters / 1000
                if dists <= 0.3 or (dists <= 2 and destuin == 0):
                    ck += 1
            elif ck == 1:
                distd = great_circle(smvp, destm).meters / 1000
                if distd <= 0.3 or (distd <= 2 and destuin == lmvp):
                    ck += 1
                    break

        if ck == 2:
            overlap = (
                great_circle(sourcem, destm).meters / 1000 / distance_going)
            if overlap > 1:
                overlap = 1 / overlap
            oow = distd + dists
            cval = overlap * 0.85 - oow * 0.15
            values.append(cval)
    if values:
        return sorted(values)[-1]
    return -1


def make_pool(mreq):
    # match requests within a 10 minutes span
    min10 = datetime.timedelta(minutes=10)
    later = mreq.moment + min10
    earlier = mreq.moment - min10
    reqs = CabRequest.objects.filter(
        moment__gte=earlier,
        moment__lte=later)
    # exclude my own requests
    reqs = reqs.exclude(profile=mreq.profile)
    # exclude me after other users prefs
    if mreq.profile.gender == Profile.GENDER.FEMALE:
        reqs = reqs.exclude(gender=Profile.GENDER.MALE)
    elif mreq.profile.gender == Profile.GENDER.MALE:
        reqs = reqs.exclude(gender=Profile.GENDER.FEMALE)
    # exclude others after my gender prefs
    if mreq.gender == Profile.GENDER.FEMALE:
        reqs = reqs.exclude(profile__gender=Profile.GENDER.MALE)
    elif mreq.gender == Profile.GENDER.MALE:
        reqs = reqs.exclude(profile__gender=Profile.GENDER.FEMALE)

    reqs = reqs.exclude(
        id__in=RequestMatch.objects.values('request2').filter(request1=mreq)
    ).exclude(id=mreq.id)

    # A to B
    calculate_matches(mreq, reqs)
    # the other way around: B to A
    for req in reqs:
        calculate_matches(req, [mreq])


def calculate_matches(mreq, reqs):
    distance_going = great_circle(
        gf(mreq.destination), gf(mreq.origin)).meters / 1000
    routes = []
    for r in mreq.routes.all():
        if not routes:
            t = r.duration
            mvpoints = [gf(mreq.origin)]
            for step in r.steps.all():
                point = gf(step.end)
                mvpoints.append(point)
            routes.append(mvpoints)
        else:
            if abs(t - r.duration) < 600:
                mvpoints = [gf(s.end) for s in r.steps.all()]
                routes.append(mvpoints)

    for r in reqs:
        route_overlap = calculate_distance(r, routes, distance_going)
        affinity = calculate_affinity(mreq.profile, r.profile)
        rm = RequestMatch(
            request1=mreq,
            request2=r,
            route_overlap=route_overlap,
            affinity=affinity)
        rm.save()


def calculate_affinity(p1, p2):
    score = 0.0

    # reckon hometown
    if hasattr(p1, 'hometown') and hasattr(p2, 'hometown'):
        if p1.hometown.hometown_id == p2.hometown.hometown_id:
            score += 2

    # reckon education
    p1_schools = [x.school_id for x in p1.education_set.all()]
    p2_schools = [x.school_id for x in p2.education_set.all()]
    mutual = len(set(p1_schools).intersection(set(p2_schools)))
    if mutual > 0:
        score += 6

    # reckon friends
    p1_friends = [x.friend_id for x in p1.friend_set.all()]
    p2_friends = [x.friend_id for x in p2.friend_set.all()]
    mutual = len(set(p1_friends).intersection(set(p2_friends)))
    if mutual > 0:
        if mutual >= 17:
            score += 10
        else:
            score += math.ceil(5 + 0.25 * (mutual - 1))

    return score
