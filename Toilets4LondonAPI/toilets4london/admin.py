from django.contrib import admin
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser, Rating
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from collections import Counter
from django.db.models import Avg


class ToiletResource(resources.ModelResource):
    class Meta:
        model = Toilet


class RatingResource(resources.ModelResource):
    class Meta:
        model = Rating


class Toilets4LondonUserResource(resources.ModelResource):
    class Meta:
        model = Toilets4LondonUser


@admin.register(Toilet)
class ToiletAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name','address', 'borough','owner','opening_hours','wheelchair', 'ratings','average_rating')
    resource_class = ToiletResource
    list_filter = ('borough', 'owner', 'wheelchair')
    search_fields = ('id', 'name', 'address')

    def ratings(self, obj):
        ratings = Rating.objects.filter(toilet=obj)
        ratings = Counter(ratings.values_list("rating", flat=True))
        return {f"{star}_star": count for star, count in ratings.items()}

    def average_rating(self, obj):
        result = Rating.objects.filter(toilet=obj).aggregate(Avg("rating"))
        return result["rating__avg"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    resource_class = RatingResource


@admin.register(Toilets4LondonUser)
class Toilets4LondonUserAdmin(admin.ModelAdmin):
    resource_class = Toilets4LondonUserResource
