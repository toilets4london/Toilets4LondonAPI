from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Toilets4LondonUser
from Toilets4LondonAPI.toilets4london.serializers import ToiletSerializer, UserSerializer, RatingSerializer
from Toilets4LondonAPI.toilets4london.permissions import IsAdminUserOrReadOnly, IsReviewerOrAdmin

from rest_framework import permissions, viewsets, status, filters, renderers, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse


# This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
class ToiletViewSet(viewsets.ModelViewSet):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminUserOrReadOnly]
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


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Toilets4LondonUser.objects.all()
    serializer_class = UserSerializer


class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReviewerOrAdmin]
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        queryset = Rating.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)