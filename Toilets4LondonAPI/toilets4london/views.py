from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Report
from Toilets4LondonAPI.toilets4london.throttling import PostAnonymousRateThrottle, GetAnonymousRateThrottle
from Toilets4LondonAPI.toilets4london.serializers import ToiletSerializer, RatingSerializer, ReportSerializer
from Toilets4LondonAPI.toilets4london.permissions import IsOwnerOrReadOnly
from Toilets4LondonAPI.toilets4london.pagination import LargeResultsSetPagination

from rest_framework import permissions, viewsets, status, filters, renderers
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver

from django_rest_passwordreset.signals import reset_password_token_created


class ToiletViewSet(viewsets.ModelViewSet):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['borough', 'latitude', 'longitude', 'name']
    search_fields = ['address', 'name', 'borough']
    pagination_class = LargeResultsSetPagination
    throttle_classes = [GetAnonymousRateThrottle]

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
        return Response({"toilets": queryset, "base_url": reverse('toilet-list')}, template_name='toilet_map.html')


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    throttle_classes = [GetAnonymousRateThrottle, PostAnonymousRateThrottle]
    serializer_class = RatingSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    throttle_classes = [GetAnonymousRateThrottle, PostAnonymousRateThrottle]
    serializer_class = ReportSerializer



@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    msg = EmailMultiAlternatives(
        # title:
        "Reset your Toilets4London password",
        # message:
        "Your unique reset token is {}".format(reset_password_token.key),
        # from:
        "noreply@toilets4london.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.send()
