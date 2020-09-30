from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import Toilets4LondonUserManager
from Toilets4LondonAPI.settings import AUTH_USER_MODEL


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
    latitude = models.FloatField()
    longitude = models.FloatField()
    owner = models.ForeignKey(AUTH_USER_MODEL, related_name='toilets', on_delete=models.CASCADE)
    opening_hours = models.CharField(max_length=500, blank=True, default='')
    name = models.CharField(max_length=500, blank=True, default='')
    wheelchair = models.BooleanField(blank=True, default=False)
    baby_change = models.BooleanField(blank=True, default=False)

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
