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

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    toilet = models.ForeignKey(Toilet, on_delete=models.CASCADE, related_name='toilet')
    rating = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, blank=False)
