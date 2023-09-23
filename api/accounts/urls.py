from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)


app_name = "api_accounts"
urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    path("verify/", views.VerifyOTPCodeAPIView.as_view(), name="verify"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]
