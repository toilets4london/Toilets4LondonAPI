from django.db import models


class Toilet(models.Model):
    address = models.CharField(max_length=500, blank=True, default='')
    borough = models.CharField(max_length=100, blank=True, default='')



