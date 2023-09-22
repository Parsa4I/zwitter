from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, OTPCodeSerializer
from django.contrib.auth import get_user_model
from accounts import tasks
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from accounts.models import OTPCode
from rest_framework.serializers import ValidationError


class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            tasks.send_otp_code_task.delay(data["email"])
            cache.set(data["email"], data["password1"], 60 * 2)
            return Response(
                {
                    "message": "OTP code has been sent to your email address.",
                },
                status.HTTP_200_OK,
            )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class VerifyOTPCodeAPIView(APIView):
    def post(self, request):
        serializer = OTPCodeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = data["email"]
            code = data["otp_code"]
            password = cache.get(email)
            try:
                otp = OTPCode.objects.get(email=email)
                if otp.code == code:
                    get_user_model().objects.create_user(email=email, password=password)
                    return Response(
                        {"message": "User registered successfully."}, status.HTTP_200_OK
                    )
                raise ValidationError("Invalid OTP code.")
            except OTPCode.DoesNotExist:
                raise ValidationError("Invalid OTP code.")
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
