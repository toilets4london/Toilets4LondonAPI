from django.contrib import admin
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser, Rating

admin.site.register(Toilets4LondonUser)
admin.site.register(Toilet)
admin.site.register(Rating)