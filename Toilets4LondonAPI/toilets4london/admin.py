from django.contrib import admin
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser, Rating, Report
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


class ReportResource(resources.ModelResource):
    class Meta:
        model = Rating


class Toilets4LondonUserResource(resources.ModelResource):
    class Meta:
        model = Toilets4LondonUser


@admin.register(Toilet)
class ToiletAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'data_source', 'address', 'borough', 'opening_hours', 'wheelchair', 'baby_change',
                    'fee', 'covid', 'rating', 'num_ratings', 'open')
    resource_class = ToiletResource
    list_filter = ('borough', 'wheelchair', 'baby_change', 'data_source', 'open')
    search_fields = ('id', 'name', 'address')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            is_superuser = request.user.is_superuser
            is_owner = (request.user == obj.owner)
            if not (is_superuser or is_owner):
                for field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):

    date_hierarchy = 'date'
    resource_class = RatingResource
    list_display = ('id',
                    'toilet',
                    'rating',
                    'date')
    search_fields = ('toilet','date')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            if not request.user.is_superuser:
                for field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form



@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    resource_class = ReportResource
    list_display = ('id',
                    'toilet',
                    'reason',
                    'other_description',
                    'date')
    search_fields = ('toilet','other_description','date')

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

    def save_model(self, request, obj, form, change):
        if obj.id:
            orig_obj = Toilets4LondonUser.objects.get(id=obj.id)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()
