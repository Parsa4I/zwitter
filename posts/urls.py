from django.urls import path
from . import views


app_name = "posts"
urlpatterns = [
    path("", views.PostsListView.as_view(), name="posts"),
    path("create-post/", views.CreatePostView.as_view(), name="create_post"),
    path(
        "create-post/attach-picture/",
        views.AttachPictureView.as_view(),
        name="attach_picture",
    ),
    path(
        "create-post/attach-video/",
        views.AttachVideoView.as_view(),
        name="attach_video",
    ),
    path(
        "post-detail/<int:pk>/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path("tag/<str:title>/", views.TagPostView.as_view(), name="tag"),
    path("like/<int:pk>/", views.LikePostView.as_view(), name="like"),
    path("reply/<int:pk>/", views.ReplyView.as_view(), name="reply"),
    path("repost/<int:pk>/", views.RepostView.as_view(), name="repost"),
    path("delete-post/<int:pk>/", views.DeletePostView.as_view(), name="delete_post"),
]
