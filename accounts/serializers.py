from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from .models import User


class CustomAuthTokenSerializer(AuthTokenSerializer):
    username = serializers.CharField(label="Username or Email")

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")

        if not user.check_password(password):
            msg = "Unable to log in with provided credentials."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
