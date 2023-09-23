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
]
