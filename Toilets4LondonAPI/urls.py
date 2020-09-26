from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from Toilets4LondonAPI.toilets4london import views
from django.contrib.auth import views as auth_views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.get_api_root_view().cls.__name__ = "LondonToiletsApiRoot"
router.get_api_root_view().cls.__doc__ = "Browse the Toilets4London API"

router.register(r'toilets', views.ToiletViewSet)
router.register(r'ratings', views.RatingViewSet, basename='')

admin.site.site_header = 'Toilets4London Toilet Admin Site'


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
]
