from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Toilets4LondonAPI.toilets4london import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.get_api_root_view().cls.__name__ = "LondonToiletsApiRoot"
router.get_api_root_view().cls.__doc__ = "Browse the Toilets4London API"

# router.register(r'users', views.UserViewSet)
router.register(r'toilets', views.ToiletViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]