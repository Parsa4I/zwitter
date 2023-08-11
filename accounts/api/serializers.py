from rest_framework import serializers
from accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import ValidationError


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        return token


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["password"] == attrs["confirm_password"]:
            return attrs
        raise ValidationError("Passwords must match.")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")


class VerifySerializer(serializers.Serializer):
    otp_code = serializers.IntegerField()
