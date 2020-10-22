from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import Toilets4LondonUserManager
from Toilets4LondonAPI.settings import AUTH_USER_MODEL
import ssl
import certifi
import geopy.geocoders as geo


def geocode(location_name):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geo.options.default_ssl_context = ctx
    geolocator = geo.Nominatim(user_agent="toilets4london")
    location = geolocator.geocode(location_name)
    return location.latitude, location.longitude


def reverse_geocode(lat,long):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geo.options.default_ssl_context = ctx
    geolocator = geo.Nominatim(user_agent="toilets4london")
    location = geolocator.reverse("%s, %s"%(str(lat),str(long)))
    return location.address


def get_borough(address):
    with open("Toilets4LondonAPI/toilets4london/boroughs.txt", "r") as borough_list:
        boroughs = borough_list.read().split(", ")
        for b in boroughs:
            if b in address:
                return b
    return ""


class Toilets4LondonUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = Toilets4LondonUserManager()

    def __str__(self):
        return self.email


class Toilet(models.Model):
    address = models.CharField(max_length=500, blank=True, default='')
    borough = models.CharField(max_length=100, blank=True, default='')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    data_source = models.CharField(max_length=500, blank=True, default='')
    owner = models.ForeignKey(AUTH_USER_MODEL, related_name='toilets', on_delete=models.CASCADE)
    opening_hours = models.CharField(max_length=500, blank=True, default='')
    name = models.CharField(max_length=500, blank=True, default='')
    wheelchair = models.BooleanField(blank=True, default=False)
    baby_change = models.BooleanField(blank=True, default=False)
    fee = models.CharField(max_length=100, blank=True, default='Free')
    covid = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        constraints = [
            models.CheckConstraint(name="Address or Coords provided", check=(
                    (models.Q(latitude__isnull=False) and models.Q(longitude__isnull=False)) or models.Q(address__isblank=False)
            ))
        ]

    def save(self, *args, **kwargs):
        nocoords = not self.latitude or not self.longitude
        noaddr = not self.address
        neither = nocoords and noaddr
        if not self.id:
            if neither:
                raise ValidationError("Must have at least an address or cooordinates")
            elif nocoords:
                try:
                    self.latitude, self.longitude = geocode(self.address)
                except:
                    raise ValidationError("Invalid cooordinates")
            elif noaddr:
                try:
                    self.address = reverse_geocode(self.latitude, self.longitude)
                except:
                    raise ValidationError("Invalid address")
            if not self.borough:
                self.borough = get_borough(self.address)
        super(Toilet, self).save(*args, **kwargs)


    def __str__(self):
        if len(self.name) > 0:
            return self.name
        else:
            return str(self.pk)


class Rating(models.Model):
    SCORE_CHOICES = zip(range(1,6), range(1,6))

    class Meta:
        unique_together = [
            'user',
            'toilet']

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    toilet = models.ForeignKey(Toilet, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "toilet %s rated %s"%(self.toilet.__str__(), self.date.strftime("%m/%d/%Y, %H:%M:%S"))


class Report(models.Model):

    DOES_NOT_EXIST = 'DNE'
    NO_TOILET_PAPER = 'NTP'
    LONG_QUEUE = 'LQ'
    NO_HANDWASHING = 'NH'
    BROKEN_OR_BLOCKED = 'BOB'
    NOT_CLEAN = 'NC'
    OTHER = "O"

    REASON_CHOICES = [
        (DOES_NOT_EXIST, 'Toilet_does_not_exist'),
        (NO_TOILET_PAPER, 'No_toilet_paper'),
        (LONG_QUEUE, 'Long_queue'),
        (NO_HANDWASHING, 'Insufficient_hand_washing_facilities'),
        (BROKEN_OR_BLOCKED, 'Toilet_blocked_or_broken'),
        (NOT_CLEAN, 'Facilities_not_clean'),
        (OTHER, 'Other'),
    ]

    reason = models.CharField(
        max_length=3,
        choices=REASON_CHOICES,
        blank=False
    )

    other_description = models.TextField(blank=True, default="")
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    toilet = models.ForeignKey(Toilet, on_delete=models.CASCADE, related_name='reports')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            'user',
            'toilet']

    def __str__(self):
        return "toilet %s reported %s" % (self.toilet.__str__(), self.date.strftime("%m/%d/%Y, %H:%M:%S"))
