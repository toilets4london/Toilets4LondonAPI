from Toilets4LondonAPI.toilets4london.models import Toilet, Rating
from Toilets4LondonAPI.toilets4london.serializers import ToiletSerializer, RatingSerializer
from Toilets4LondonAPI.toilets4london.permissions import IsOwnerOrReadOnly

from rest_framework import permissions, viewsets, status, filters, renderers, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse


# This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
class ToiletViewSet(viewsets.ModelViewSet):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['borough', 'latitude','longitude','name']
    search_fields = ['address', 'name', 'borough']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=False, methods=['get'], renderer_classes=[renderers.TemplateHTMLRenderer])
    def view_map(self, request):
        queryset = Toilet.objects.all()
        return Response({"toilets": queryset,"base_url": reverse('toilet-list')}, template_name='toilet_map.html')


class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

