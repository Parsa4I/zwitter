from django.urls import path, include


urlpatterns = [
    path("accounts/", include("api.accounts.urls")),
    path("posts/", include("api.posts.urls")),
]
