from rest_framework import serializers
from .validators import validate_unique_email


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, validators=[validate_unique_email])
    password1 = serializers.CharField(min_length=4, max_length=255)
    password2 = serializers.CharField(min_length=4, max_length=255)

    def validate(self, attrs):
        pass1 = attrs.get("password1")
        pass2 = attrs.get("password2")
        if pass1 and pass2 and pass1 != pass2:
            raise serializers.ValidationError("Passwords must match.")
        return attrs


class OTPCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    otp_code = serializers.IntegerField(min_value=1000, max_value=9999)
