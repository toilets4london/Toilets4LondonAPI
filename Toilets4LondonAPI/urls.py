from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from Toilets4LondonAPI.toilets4london import views

urlpatterns = [
    path('toilets/', views.ToiletList.as_view()),
    path('toilets/<int:pk>/', views.ToiletDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
