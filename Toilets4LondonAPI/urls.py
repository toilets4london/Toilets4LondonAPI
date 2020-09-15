from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Toilets4LondonAPI.toilets4london import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'toilets', views.ToiletViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]