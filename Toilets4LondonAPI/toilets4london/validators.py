from django.core.exceptions import ValidationError


def validate_latitude(value):
    if value < -90 or value > 90:
        raise ValidationError("Latitude must be between -90 and 90")


def validate_longitude(value):
    if value < -180 or value > 180:
        raise ValidationError("Longitude must be between -180 and 180")