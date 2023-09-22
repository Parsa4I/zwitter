from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError


def validate_unique_email(value):
    if get_user_model().objects.filter(email=value).exists():
        raise ValidationError("Email address is already in use.")
    return value
