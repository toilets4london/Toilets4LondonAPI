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
    readonly_fields = [
        'id','owner'
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        is_owner = (request.user == obj.owner)
        if not (is_superuser or is_owner):
            for field in form.base_fields:
                field.disabled = True
        return form

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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions'
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form
