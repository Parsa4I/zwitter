from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from posts.models import Post, Tag
from .serializers import PostSerializer
from accounts.models import User
from django.shortcuts import get_object_or_404


class PostAPIView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data)


class PostsListAPIView(generics.GenericAPIView):
    def get(self, request):
        posts = Post.objects.all()
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class UserPostsListAPIView(generics.GenericAPIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        posts = Post.objects.filter(user=user)
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class TagPostsAPIView(generics.GenericAPIView):
    def get(self, request, title):
        tag = get_object_or_404(Tag, title=title)
        posts = tag.posts.all()
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
