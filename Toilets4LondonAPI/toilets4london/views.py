from Toilets4LondonAPI.toilets4london.models import Toilet
from Toilets4LondonAPI.toilets4london.serializers import ToiletSerializer
from rest_framework import generics


# https://www.django-rest-framework.org/tutorial/3-class-based-views/


class ToiletList(generics.ListCreateAPIView):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer