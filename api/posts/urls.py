from django.urls import path
from . import views


app_name = "api_posts"
urlpatterns = [
    path("", views.PostsListAPIView.as_view(), name="posts_list"),
    path("<int:pk>/", views.PostAPIView.as_view(), name="post_detail"),
    path("user/<int:pk>/", views.UserPostsListAPIView.as_view(), name="user_posts"),
    path("tag/<str:title>/", views.TagPostsAPIView.as_view(), name="tag_posts"),
    path("create/", views.PostCreateAPIView.as_view(), name="create"),
    path("repost/<int:pk>/", views.RepostAPIView.as_view(), name="repost"),
    path("reply/<int:pk>/", views.ReplyAPIView.as_view(), name="reply"),
    path("like/<int:pk>/", views.LikePostAPIView.as_view(), name="like"),
    path("delete/<int:pk>/", views.DeletePostAPIView.as_view(), name="delete"),
    path("update/<int:pk>/", views.UpdatePostAPIView.as_view(), name="updaet"),
    path("is-liked/<int:pk>/", views.IsLikedAPIView.as_view(), name="is_liked"),
]
