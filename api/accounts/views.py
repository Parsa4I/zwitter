from rest_framework.views import APIView
from .serializers import (
    UserRegisterSerializer,
    OTPCodeSerializer,
    UserSerializer,
    FollowRequestSerializer,
    FollowingSerializer,
)
from django.contrib.auth import get_user_model
from accounts import tasks
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from accounts.models import OTPCode
from rest_framework.serializers import ValidationError
from accounts.models import User, Following
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


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


class UserAPIView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data, status.HTTP_200_OK)


class ChangeUsernameAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user
        username = request.data.get("username")
        if username is None:
            raise ValidationError({"error": "username field is required."})
        user.username = username
        user.save()
        return Response({"message": "Username updated."}, status.HTTP_200_OK)


class IsFollowedAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        followed = get_object_or_404(User, pk=pk)
        if Following.objects.filter(
            followed=followed, follower=request.user, accepted=True
        ).exists():
            return Response({"is_followed": True}, status.HTTP_200_OK)
        return Response({"is_followed": False}, status.HTTP_200_OK)


class FollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        follower = request.user
        followed = get_object_or_404(User, pk=pk)
        if followed == follower:
            return Response(
                {"message": "You cannot follow yourself."}, status.HTTP_409_CONFLICT
            )
        following, created = Following.objects.get_or_create(
            follower=follower, followed=followed
        )
        if not created:
            if following.accepted:
                return Response(
                    {"message": "You are following this user."},
                    status.HTTP_409_CONFLICT,
                )
            return Response(
                {"message": "You have already sent a follow request to this user."},
                status.HTTP_409_CONFLICT,
            )
        return Response({"message": "Follow request sent."}, status.HTTP_200_OK)


class UnfollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        follower = request.user
        followed = get_object_or_404(User, pk=pk)
        if followed == follower:
            return Response(
                {"message": "You cannot unfollow yourself."}, status.HTTP_409_CONFLICT
            )
        try:
            following = Following.objects.get(
                follower=follower, followed=followed, accepted=True
            )
            following.delete()
            return Response({"message": "Unfollowed."}, status.HTTP_200_OK)
        except Following.DoesNotExist:
            try:
                following = Following.objects.get(
                    follower=follower, followed=followed, accepted=False
                )
                following.delete()
                return Response(
                    {"message": "Follow request canceled."}, status.HTTP_200_OK
                )
            except Following.DoesNotExist:
                return Response(
                    {"message": "You are have not been following this user."},
                    status.HTTP_200_OK,
                )


class FollowRequestsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        follow_requests = Following.objects.filter(
            followed=request.user, accepted=False
        )
        serializer = FollowRequestSerializer(follow_requests, many=True)
        return Response(serializer.data)


class FollowingAPIView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        following = Following.objects.filter(follower=user, accepted=True)
        serializer = FollowingSerializer(
            following, many=True, context={"request": request}
        )
        return Response(serializer.data, status.HTTP_200_OK)


class FollowersAPIView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        following = Following.objects.filter(followed=user, accepted=True)
        serializer = FollowingSerializer(
            following, many=True, context={"request": request}
        )
        return Response(serializer.data, status.HTTP_200_OK)


class AcceptFollowRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        follower = get_object_or_404(User, pk=pk)
        follow_request = get_object_or_404(
            Following, follower=follower, followed=request.user
        )
        if not follow_request.accepted:
            follow_request.accepted = True
            follow_request.save()
            return Response({"message": "Follow request accepted."}, status.HTTP_200_OK)
        return Response(
            {"message": "Follow request had been accepted before."}, status.HTTP_200_OK
        )


class DeclineFollowRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        follower = get_object_or_404(User, pk=pk)
        follow_request = get_object_or_404(
            Following, follower=follower, followed=request.user, accepted=False
        )
        follow_request.delete()
        return Response({"message": "Follow request declined."}, status.HTTP_200_OK)
