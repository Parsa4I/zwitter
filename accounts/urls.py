from django.urls import path
from . import views


app_name = "accounts"
urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="user_register"),
    path("verify/", views.Verify.as_view(), name="verify"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/", views.UserPasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password-reset/done/",
        views.UserPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.UserPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path(
        "change-username/",
        views.ChangeUsernameView.as_view(),
        name="change_username",
    ),
    path("follow/<int:pk>/", views.FollowView.as_view(), name="follow"),
    path(
        "follow-requests/",
        views.FollowRequests.as_view(),
        name="follow_requests",
    ),
    path("accept-follow/<int:pk>/", views.AcceptFollow.as_view(), name="accept_follow"),
    path(
        "decline-follow/<int:pk>/", views.DeclineFollow.as_view(), name="decline_follow"
    ),
    path("followers/<int:pk>/", views.FollowersView.as_view(), name="followers"),
    path("following/<int:pk>/", views.FollowingView.as_view(), name="following"),
    path("mute/<int:pk>/", views.MuteView.as_view(), name="mute"),
]
