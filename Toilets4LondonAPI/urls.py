from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from Toilets4LondonAPI.toilets4london import views
from Toilets4LondonAPI.toilets4london.admin import toiletowneradmin

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.get_api_root_view().cls.__name__ = "LondonToiletsApiRoot"
router.get_api_root_view().cls.__doc__ = "Browse the Toilets4London API"

router.register(r'toilets', views.ToiletViewSet)
router.register(r'ratings', views.RatingViewSet, basename='')

admin.site.site_header = 'Toilets4London Admin Site'


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('toilet-owners/',toiletowneradmin.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
]