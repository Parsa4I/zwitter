from django.urls import path
from . import views


app_name = "api_posts"
urlpatterns = [
    path("", views.PostsListAPIView.as_view(), name="posts_list"),
    path("<int:pk>/", views.PostAPIView.as_view(), name="post_detail"),
    path("user/<int:pk>/", views.UserPostsListAPIView.as_view(), name="user_posts"),
    path("tag/<str:title>/", views.TagPostsAPIView.as_view(), name="tag_posts"),
]
