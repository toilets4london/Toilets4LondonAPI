from django.contrib import admin
from Toilets4LondonAPI.toilets4london.models import (
    Toilet,
    Toilets4LondonUser,
    Rating,
    Report,
    SuggestedToilet,
    DownloadReason,
)
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import Toilets4LondonAPI.settings as settings


class ToiletResource(resources.ModelResource):
    class Meta:
        model = Toilet


class RatingResource(resources.ModelResource):
    class Meta:
        model = Rating


class ReportResource(resources.ModelResource):
    class Meta:
        model = Rating


class Toilets4LondonUserResource(resources.ModelResource):
    class Meta:
        model = Toilets4LondonUser


class SuggestedToiletResource(resources.ModelResource):
    class Meta:
        model = SuggestedToilet


def set_open(modeladmin, request, queryset):
    queryset.update(open=True)


set_open.short_description = "Mark selected toilets as open"


def set_closed(modeladmin, request, queryset):
    queryset.update(open=False)


set_closed.short_description = "Mark selected toilets as closed"


def delete_toilet_and_report(modeladmin, request, queryset):
    for report in queryset:
        toilet = report.toilet
        report.delete()
        toilet.delete()
    modeladmin.message_user(
        request, "Selected reports and their associated toilets have been deleted."
    )


delete_toilet_and_report.short_description = (
    "Delete selected reports and associated toilets"
)


@admin.register(Toilet)
class ToiletAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "name",
        "data_source",
        "address",
        "borough",
        "opening_hours",
        "wheelchair",
        "baby_change",
        "fee",
        "covid",
        "rating",
        "num_ratings",
        "open",
    )
    resource_class = ToiletResource
    list_filter = ("borough", "wheelchair", "baby_change", "data_source", "open")
    search_fields = ("id", "name", "address", "data_source")

    actions = [set_open, set_closed]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            return []
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            is_superuser = request.user.is_superuser
            is_owner = (request.user == obj.owner) or (
                request.user.responsible_borough == obj.borough
            )
            if not (is_superuser or is_owner):
                for field in form.base_fields:
                    form.base_fields[field].disabled = True
        else:
            if "owner" in form.base_fields:
                form.base_fields["owner"].initial = request.user
                form.base_fields["owner"].disabled = True
        if not request.user.is_superuser:  # Don't let non super users change these
            if "covid" in form.base_fields:
                form.base_fields["covid"].disabled = True
            if "rating" in form.base_fields:
                form.base_fields["rating"].disabled = True
            if "num_ratings" in form.base_fields:
                form.base_fields["num_ratings"].disabled = True
            if "owner" in form.base_fields:
                form.base_fields["owner"].disabled = True
        return form

    def has_change_permission(self, request, obj=None):
        can_change = super().has_change_permission(request, obj)
        if obj is not None:
            is_superuser = request.user.is_superuser
            is_owner = (request.user == obj.owner) or (
                request.user.responsible_borough == obj.borough
            )
            if is_superuser:
                return True
            if is_owner:
                return can_change
        return False

    def has_delete_permission(self, request, obj=None):
        can_delete = super().has_delete_permission(request, obj)
        if obj is not None:
            is_superuser = request.user.is_superuser
            is_owner = (request.user == obj.owner) or (
                request.user.responsible_borough == obj.borough
            )
            if is_superuser:
                return True
            if is_owner:
                return can_delete
        return False

    class Media:
        if hasattr(settings, "MAPS_KEY") and settings.MAPS_KEY:
            css = {
                "all": ("css/admin/location_picker.css",),
            }
            js = (
                "https://maps.googleapis.com/maps/api/js?key={}&libraries=geometry,places".format(
                    settings.MAPS_KEY
                ),
                "js/admin/location_picker.js",
            )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "latitude" in request.GET and "longitude" in request.GET:
            form.base_fields["latitude"].initial = request.GET["latitude"]
            form.base_fields["longitude"].initial = request.GET["longitude"]
        return form


@admin.register(SuggestedToilet)
class SuggestedToiletAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    resource_class = RatingResource
    list_display = ("id", "latitude", "longitude", "date", "details")
    search_fields = ("details", "date", "id")

    class Media:
        if hasattr(settings, "MAPS_KEY") and settings.MAPS_KEY:
            css = {
                "all": ("css/admin/location_picker.css",),
            }
            js = (
                "https://maps.googleapis.com/maps/api/js?key={}&libraries=geometry,places".format(
                    settings.MAPS_KEY
                ),
                "js/admin/location_picker.js",
            )


@admin.register(DownloadReason)
class DownloadReasonAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    resource_class = RatingResource
    list_display = ("id", "date", "details")
    search_fields = ("details", "date", "id")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    resource_class = RatingResource
    list_display = ("id", "toilet", "rating", "date")
    search_fields = ("toilet", "date")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            if not request.user.is_superuser:
                for field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    resource_class = ReportResource
    list_display = ("id", "toilet", "reason", "other_description", "date")
    search_fields = ("toilet", "other_description", "date")

    actions = [delete_toilet_and_report]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            if not request.user.is_superuser:
                for field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form


@admin.register(Toilets4LondonUser)
class Toilets4LondonUserAdmin(admin.ModelAdmin):
    resource_class = Toilets4LondonUserResource

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                "username",
                "is_superuser",
                "user_permissions",
                "responsible_borough",
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "responsible_borough",
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    def save_model(self, request, obj, form, change):
        if obj.id:
            orig_obj = Toilets4LondonUser.objects.get(id=obj.id)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()
