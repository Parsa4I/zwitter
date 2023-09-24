from django.urls import path
from . import views


app_name = "api_posts"
urlpatterns = [
    path("<int:pk>/", views.PostAPIView.as_view(), name="post_detail"),
]
