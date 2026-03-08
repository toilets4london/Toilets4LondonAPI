from Toilets4LondonAPI.toilets4london.models import (
    Toilet,
    Rating,
    Report,
    SuggestedToilet,
    DownloadReason,
)
from Toilets4LondonAPI.toilets4london.throttling import (
    PostAnonymousRateThrottle,
    GetAnonymousRateThrottle,
)
from Toilets4LondonAPI.toilets4london.serializers import (
    ToiletSerializer,
    RatingSerializer,
    ReportSerializer,
    SuggestedToiletSerializer,
    DownloadReasonSerializer,
)
from Toilets4LondonAPI.toilets4london.permissions import (
    IsOwnerOrReadOnly,
    IsAdminOrWriteOnly,
)
from Toilets4LondonAPI.toilets4london.pagination import LargeResultsSetPagination

from rest_framework import permissions, viewsets, status, filters, renderers
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver

from django_rest_passwordreset.signals import reset_password_token_created
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import admin
from Toilets4LondonAPI.toilets4london.borough_list import BOROUGHS
from Toilets4LondonAPI.settings import MAPS_KEY


class ToiletViewSet(viewsets.ModelViewSet):
    queryset = Toilet.objects.filter(open=True)
    serializer_class = ToiletSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["borough", "latitude", "longitude", "name"]
    search_fields = ["address", "name", "borough"]
    pagination_class = LargeResultsSetPagination
    throttle_classes = [GetAnonymousRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False, methods=["get"], renderer_classes=[renderers.TemplateHTMLRenderer]
    )
    def view_map(self, request):
        queryset = Toilet.objects.all()
        return Response(
            {"toilets": queryset, "base_url": reverse("toilet-list")},
            template_name="toilet_map.html",
        )


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    throttle_classes = [GetAnonymousRateThrottle, PostAnonymousRateThrottle]
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        toilet = serializer.validated_data["toilet"]
        num_ratings = toilet.num_ratings + 1
        toilet.num_ratings = num_ratings
        if toilet.rating and num_ratings > 1:
            toilet.rating = (
                toilet.rating * (num_ratings - 1) + serializer.validated_data["rating"]
            ) / num_ratings
        else:
            toilet.rating = serializer.validated_data["rating"]
        toilet.save()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    throttle_classes = [GetAnonymousRateThrottle, PostAnonymousRateThrottle]
    serializer_class = ReportSerializer


class SuggestedToiletViewSet(viewsets.ModelViewSet):
    queryset = SuggestedToilet.objects.all()
    throttle_classes = [GetAnonymousRateThrottle, PostAnonymousRateThrottle]
    serializer_class = SuggestedToiletSerializer


class DownloadReasonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrWriteOnly]
    queryset = DownloadReason.objects.all()
    throttle_classes = [PostAnonymousRateThrottle]
    serializer_class = DownloadReasonSerializer


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
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
        [reset_password_token.user.email],
    )
    msg.send()


@method_decorator(staff_member_required, name="dispatch")
class PrefillToiletFormView(View):
    template_name = "admin/toilets4london/toilet/add_form.html"

    def get(self, request, *args, **kwargs):
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        context = {
            "form": admin.site._registry[Toilet].get_form(request)(),
            "latitude": latitude,
            "longitude": longitude,
        }
        return render(request, self.template_name, context)


@method_decorator(staff_member_required, name="dispatch")
class ReviewSuggestionsView(View):
    def get(self, request):
        suggestions = SuggestedToilet.objects.all().order_by("-date")
        suggestions_data = [
            {
                "id": s.id,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "details": s.details,
                "date": s.date.strftime("%Y-%m-%d %H:%M"),
            }
            for s in suggestions
        ]
        context = {
            "suggestions_json": json.dumps(suggestions_data),
            "suggestions_count": suggestions.count(),
            "boroughs": BOROUGHS,
            "maps_key": MAPS_KEY,
        }
        return render(request, "review_suggestions.html", context)


@method_decorator(staff_member_required, name="dispatch")
class ApproveSuggestionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            suggested_toilet_id = data.get("suggested_toilet_id")

            try:
                suggested = SuggestedToilet.objects.get(id=suggested_toilet_id)
            except SuggestedToilet.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Suggested toilet not found."},
                    status=404,
                )

            toilet = Toilet(
                latitude=float(data["latitude"]),
                longitude=float(data["longitude"]),
                owner=request.user,
                address=data.get("address", ""),
                name=data.get("name", ""),
                borough=data.get("borough", ""),
                opening_hours=data.get("opening_hours", ""),
                wheelchair=data.get("wheelchair", False),
                baby_change=data.get("baby_change", False),
                fee=data.get("fee", "Free"),
                data_source=data.get("data_source", "App upload"),
            )
            toilet.full_clean()
            toilet.save()

            suggested.delete()

            return JsonResponse({"success": True, "toilet_id": toilet.id})
        except ValidationError as e:
            return JsonResponse(
                {"success": False, "error": str(e.message_dict)},
                status=400,
            )
        except (KeyError, ValueError) as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=400,
            )


@method_decorator(staff_member_required, name="dispatch")
class DismissSuggestionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            suggested_toilet_id = data.get("suggested_toilet_id")

            try:
                suggested = SuggestedToilet.objects.get(id=suggested_toilet_id)
            except SuggestedToilet.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Suggested toilet not found."},
                    status=404,
                )

            suggested.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500,
            )
