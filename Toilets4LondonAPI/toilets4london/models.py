from django.db import models


# Toilets are always associated with a creator.
# Only authenticated users may create toilets.
# Only the creator of a toilet may update or delete it.
# Unauthenticated requests should have full read-only access.


class Toilet(models.Model):
    address = models.CharField(max_length=500, blank=True, default='')
    borough = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey('auth.User', related_name='toilets', on_delete=models.CASCADE)



