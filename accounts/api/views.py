from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    SignupSerializer,
    MyTokenObtainPairSerializer,
    UserSerializer,
    VerifySerializer,
)
from accounts.models import User, OTPCode
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from accounts.tasks import send_otp_code_task
from django.shortcuts import get_object_or_404


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            send_otp_code_task.delay(serializer.validated_data["email"])
            request.session["user_signup_info"] = {
                "email": serializer.validated_data["email"],
                "password": serializer.validated_data["password"],
            }
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAPIView(APIView):
    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        if serializer.is_valid():
            email = request.session["user_signup_info"]["email"]
            password = request.session["user_signup_info"]["password"]
            otp_code_obj = get_object_or_404(OTPCode, email=email)
            if serializer.validated_data["otp_code"] == otp_code_obj.code:
                user = User.objects.create_user(email=email, password=password)
                otp_code_obj.delete()
                return Response(UserSerializer(user).data)
            return Response({"error": "Code does not match."})
        return Response(serializer.errors)
