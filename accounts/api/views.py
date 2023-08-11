from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    SignupSerializer,
    MyTokenObtainPairSerializer,
    UserSerializer,
)
from accounts.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            return Response(UserSerializer(instance=user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
