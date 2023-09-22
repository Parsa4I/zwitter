from django.urls import path
from . import views


app_name = "api_accounts"
urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    path("verify/", views.VerifyOTPCodeAPIView.as_view(), name="verify"),
]
