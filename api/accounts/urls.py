from django.urls import path, include
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from django_rest_passwordreset.views import (
    reset_password_confirm,
    reset_password_request_token,
    reset_password_validate_token,
)


app_name = "api_accounts"
urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    path("verify/", views.VerifyOTPCodeAPIView.as_view(), name="verify"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path(
        "password-reset/validate_token/",
        reset_password_validate_token,
        name="reset_password_validate",
    ),
    path(
        "password-reset/confirm/", reset_password_confirm, name="reset_password_confirm"
    ),
    path(
        "password-reset/", reset_password_request_token, name="reset_password_request"
    ),
    path("user/<int:pk>/", views.UserAPIView.as_view(), name="user"),
    path(
        "update-username/",
        views.ChangeUsernameAPIView.as_view(),
        name="update_username",
    ),
    path(
        "is-followed/<int:pk>/", views.IsFollowedAPIView.as_view(), name="is_followed"
    ),
    path("follow/<int:pk>/", views.FollowAPIView.as_view(), name="follow"),
    path("unfollow/<int:pk>/", views.UnfollowAPIView.as_view(), name="unfollow"),
    path(
        "follow-requests/",
        views.FollowRequestsAPIView.as_view(),
        name="follow_requests",
    ),
    path("following/<int:pk>/", views.FollowingAPIView.as_view(), name="following"),
    path("followers/<int:pk>/", views.FollowersAPIView.as_view(), name="followers"),
    path(
        "accept-follow/<int:pk>/",
        views.AcceptFollowRequestAPIView.as_view(),
        name="accept_follow_request",
    ),
    path(
        "decline-follow/<int:pk>/",
        views.DeclineFollowRequestAPIView.as_view(),
        name="decline_follow_request",
    ),
    # path('mute/<int:pk>/',),
    # path('is-followed',),
]
