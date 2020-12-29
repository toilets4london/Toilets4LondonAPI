from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import Toilets4LondonUserManager
from Toilets4LondonAPI.settings import AUTH_USER_MODEL
from Toilets4LondonAPI.toilets4london.borough_list import BOROUGHS
from Toilets4LondonAPI.toilets4london.validators import validate_latitude, validate_longitude


class Toilets4LondonUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = Toilets4LondonUserManager()

    def __str__(self):
        return self.email


class Toilet(models.Model):

    borough_choices = [(b, b) for b in BOROUGHS] + [("", "Other")]

    # Required fields
    latitude = models.FloatField(blank=False, validators=[validate_latitude])
    longitude = models.FloatField(blank=False, validators=[validate_longitude])
    owner = models.ForeignKey(AUTH_USER_MODEL, related_name='toilets', on_delete=models.CASCADE)
    borough = models.CharField(choices=borough_choices, default="", max_length=100)

    # Optional fields
    name = models.CharField(blank=True, max_length=500, default='')
    data_source = models.CharField(blank=True, max_length=500, default='')
    address = models.CharField(blank=True, max_length=500, default='')
    opening_hours = models.CharField(blank=True, max_length=500, default='')
    covid = models.CharField(blank=True, max_length=500, default='')

    wheelchair = models.BooleanField(blank=True, default=False)
    baby_change = models.BooleanField(blank=True, default=False)
    open = models.BooleanField(blank=True, default=True)

    fee = models.CharField(blank=True, max_length=100, default='Free')
    num_ratings = models.IntegerField(blank=True, default=0)

    # Nullable fields
    rating = models.FloatField(blank=True, null=True)

    def __str__(self):
        if len(self.name) > 0:
            return self.name
        else:
            return str(self.pk)


class Rating(models.Model):
    SCORE_CHOICES = zip(range(1,6), range(1,6))

    toilet = models.ForeignKey(Toilet, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "toilet %s rated %s"%(self.toilet.__str__(), self.date.strftime("%m/%d/%Y, %H:%M:%S"))


class Report(models.Model):

    REASON_CHOICES = [
        ('DNE', 'This toilet does not exist'),
        ('O', 'Other')
    ]

    reason = models.CharField(
        max_length=3,
        choices=REASON_CHOICES,
        blank=False
    )

    other_description = models.TextField(blank=True, default="", max_length=500)
    toilet = models.ForeignKey(Toilet, on_delete=models.CASCADE, related_name='reports')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "toilet %s reported %s" % (self.toilet.__str__(), self.date.strftime("%m/%d/%Y, %H:%M:%S"))
