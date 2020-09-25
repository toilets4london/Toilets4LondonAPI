from django.contrib import admin
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser, Rating
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ToiletResource(resources.ModelResource):
    class Meta:
        model = Toilet


class RatingResource(resources.ModelResource):
    class Meta:
        model = Rating


class ToiletAdmin(ImportExportModelAdmin):
    resource_class = ToiletResource


class RatingAdmin(ImportExportModelAdmin):
    resource_class = RatingResource


admin.site.register(Toilets4LondonUser)
admin.site.register(Toilet, ToiletAdmin)
admin.site.register(Rating, RatingAdmin)